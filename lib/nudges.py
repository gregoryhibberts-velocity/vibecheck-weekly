"""Follow-up emails for free sign-ups. Day 0 (report link) is sent at sign-up by the email gate.
Day 2: reminder to unlock the full report. Day 5: offer of the weekly plan.
Each (email, kind) is sent at most once (email_sends table). Paid users and unsubscribed users are skipped."""
import hmac, hashlib, html, urllib.parse
from . import config, db, mailer, crm
DAY = 86400
MAX_AGE = 30 * DAY  # don't nudge sign-ups older than this
E = html.escape

def unsub_token(email):
    return hmac.new(("unsub:" + (config.CRON_SECRET or "")).encode(), email.lower().encode(), hashlib.sha256).hexdigest()[:32]
def unsub_url(email):
    return f"{config.BASE_URL}/unsubscribe?" + urllib.parse.urlencode({"e": email, "t": unsub_token(email)})
def check_unsub(email, tok): return bool(config.CRON_SECRET and email and tok and hmac.compare_digest(unsub_token(email), tok))
def do_unsubscribe(email):
    email = email.lower()
    if not db.one("SELECT email FROM unsubscribes WHERE email=?", (email,)):
        db.q("INSERT INTO unsubscribes(email, created_at) VALUES(?,?)", (email, db.now()))
    crm.unsubscribe(email)

def sync_unsubscribes():
    """Two-way sync between the local unsubscribes table and the Resend audience (unsubscribed=true)."""
    local = {r["email"].lower() for r in db.all("SELECT email FROM unsubscribes")}
    contacts = crm.list_contacts() if crm._ok() else []
    remote = {c["email"].lower() for c in contacts if c.get("unsubscribed")}
    pulled = sorted(remote - local)
    for e in pulled: db.q("INSERT INTO unsubscribes(email, created_at) VALUES(?,?)", (e, db.now()))
    pushed = sorted(e for e in local - remote if crm.unsubscribe(e))
    return {"local_added": len(pulled), "resend_updated": len(pushed), "unsubscribed": sorted(local | remote)}

def _wrap(paras, button, email):
    u = unsub_url(email)
    body = "".join(f"<p style='margin:0 0 14px'>{p}</p>" for p in paras)
    h = (f"<div style='font-family:Arial,sans-serif;font-size:15px;line-height:1.5;color:#1f2937;max-width:560px'>{body}"
         f"<p style='margin:20px 0'><a href='{E(button[1])}' style='background:#2563eb;color:#fff;padding:11px 18px;border-radius:6px;text-decoration:none'>{E(button[0])}</a></p>"
         f"<p style='margin:0 0 14px'>VibeCheck Weekly</p>"
         f"<p style='font-size:12px;color:#6b7280'>You are receiving this because you requested a free scan at vibecheck.itsvelocitygroup.com. "
         f"<a href='{E(u)}' style='color:#6b7280'>Unsubscribe</a></p></div>")
    import re
    t = "\n\n".join(re.sub("<[^>]+>", "", p) for p in paras) + f"\n\n{button[0]}: {button[1]}\n\nVibeCheck Weekly\n\nUnsubscribe: {u}\n"
    return h, t, {"List-Unsubscribe": f"<{u}>", "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"}

def build(kind, email, host, report_url):
    host = E(host)
    if kind == "unlock":
        subj = f"Your full VibeCheck report for {host} is ready to unlock"
        paras = [f"Hello,",
                 f"A few days ago you ran a free scan of {host}. The free report shows the issue titles; the full report adds the details behind each one and step-by-step fixes you can paste into your AI builder.",
                 "You can unlock the complete report for a one-time $9."]
        return subj, *_wrap(paras, ("Unlock the full report", report_url), email)
    if kind == "plan":
        subj = f"Keep {host} checked every week"
        paras = ["Hello,",
                 f"Apps built with AI tools change quickly, and a new release can reopen a security or Google-visibility issue without anyone noticing.",
                 f"The Solo plan rescans {host} every week for $19 a month and emails you a full report each time, including anything new since the last check. You can cancel at any time."]
        return subj, *_wrap(paras, ("Start weekly checks", report_url + "/monitor"), email)

def _candidates():
    return db.all("""SELECT a.email, a.created_at, s.token, s.url FROM accounts a
        JOIN scans s ON s.id = (SELECT MAX(id) FROM scans WHERE email=a.email)
        WHERE a.plan='free' AND a.created_at > ?
          AND NOT EXISTS (SELECT 1 FROM scans p WHERE p.email=a.email AND p.unlocked=1)
          AND NOT EXISTS (SELECT 1 FROM unsubscribes u WHERE u.email=a.email)""", (db.now() - MAX_AGE,))

def _mark(email, kind):
    if db.one("SELECT id FROM email_sends WHERE email=? AND kind=?", (email, kind)): return False
    db.q("INSERT INTO email_sends(email, kind, sent_at) VALUES(?,?,?)", (email, kind, db.now())); return True

def sync_audience(limit=200):
    """Backfill / retry: add every sign-up not yet in the Resend Audience."""
    rows = db.all("""SELECT email FROM accounts a WHERE NOT EXISTS (SELECT 1 FROM email_sends e WHERE e.email=a.email AND e.kind='audience')
        AND NOT EXISTS (SELECT 1 FROM unsubscribes u WHERE u.email=a.email) ORDER BY id LIMIT ?""", (limit,))
    n = 0
    for r in rows:
        if crm.add_signup(r["email"]): _mark(r["email"], "audience"); n += 1
    return n

def run(limit=100):
    out = {"audience_added": sync_audience(), "sent": []}
    now = db.now()
    for c in _candidates():
        age = now - int(c["created_at"] or now)
        host = urllib.parse.urlparse(c["url"] or "").hostname or "your app"
        for kind, due in (("plan", 5 * DAY), ("unlock", 2 * DAY)):
            if age < due or db.one("SELECT id FROM email_sends WHERE email=? AND kind=?", (c["email"], kind)): continue
            if kind == "plan" and not db.one("SELECT id FROM email_sends WHERE email=? AND kind='unlock' AND sent_at <= ?", (c["email"], now - 2 * DAY)): continue  # keep order and spacing
            subj, h, t, hd = build(kind, c["email"], host, f"{config.BASE_URL}/r/{c['token']}")
            if _mark(c["email"], kind) and mailer.send(c["email"], subj, h, t, hd): out["sent"].append(kind)
            break  # at most one nudge per person per run
        if len(out["sent"]) >= limit: break
    return out

def send_tests(to, token=""):
    """Send one of each nudge to `to`, using a real report token if given. Does not touch send tracking."""
    sc = db.one("SELECT token, url FROM scans WHERE token=?", (token,)) if token else None
    if not sc: sc = db.one("SELECT token, url FROM scans WHERE email=? ORDER BY id DESC LIMIT 1", (to.lower(),))
    if not sc: return {"error": "no report found"}
    host = urllib.parse.urlparse(sc["url"] or "").hostname or "your app"
    res = {"report": f"{config.BASE_URL}/r/{sc['token']}"}
    for kind in ("unlock", "plan"):
        subj, h, t, hd = build(kind, to, host, f"{config.BASE_URL}/r/{sc['token']}")
        res[kind] = mailer.send(to, "[TEST] " + subj, h, t, hd)
    return res
