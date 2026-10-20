#!/usr/bin/env python3
"""Send the daily tip email to Resend audience contacts with unsubscribed=false.
Usage:  python3 scripts/send_daily_tip.py [--date YYYY-MM-DD] [--dry-run]
Env:    RESEND_API_KEY (or EMAIL_API_KEY), CRON_SECRET (same value as on Render; used for unsubscribe links
        and the /api/cron/unsub-sync call). Optional: RESEND_AUDIENCE_ID, BASE_URL, DAILY_LOG.
Once-per-day guard: refuses to send if DAILY_LOG already has a 'sent' row for that date.
Each run first syncs local unsubscribes <-> Resend via the live site, then re-reads the audience."""
import os, sys, csv, json, argparse, datetime, html, fcntl
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
os.environ.setdefault("EMAIL_API_KEY", os.environ.get("RESEND_API_KEY", ""))
os.environ.setdefault("RESEND_AUDIENCE_ID", "c736e543-7792-4024-bfe9-7d003f4fe935")
from lib import config, http, tips, crm, nudges
FROM = "VibeCheck Weekly <hello@vibecheck.itsvelocitygroup.com>"
REPLY_TO = "vibecheckweekly@mail.grokbot.com"
LOG = os.environ.get("DAILY_LOG", "/workspace/marketing/daily_emails.csv")
FIELDS = ["date", "slug", "subject", "status", "recipients", "sent", "failed", "skipped_unsubscribed", "logged_at"]

def already_sent(day):
    if not os.path.exists(LOG): return False
    with open(LOG) as f: return any(r["date"] == day and r["status"] == "sent" for r in csv.DictReader(f))
def log(row):
    new = not os.path.exists(LOG)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        if new: w.writeheader()
        w.writerow({**row, "logged_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")})
def build(t, email):
    u = nudges.unsub_url(email)
    h = (f"<div style='font-family:Arial,sans-serif;font-size:15px;line-height:1.5;color:#1f2937;max-width:560px'>"
         + "".join(f"<p style='margin:0 0 14px'>{html.escape(p)}</p>" for p in t["body"])
         + f"<p style='margin:20px 0'><a href='{config.BASE_URL}/' style='background:#2563eb;color:#fff;padding:11px 18px;border-radius:6px;text-decoration:none'>Run a free scan</a></p>"
         + f"<p style='margin:0 0 14px'>VibeCheck Weekly</p><p style='font-size:12px;color:#6b7280'>You are receiving this because you requested a free scan at vibecheck.itsvelocitygroup.com. "
         + f"<a href='{html.escape(u)}' style='color:#6b7280'>Unsubscribe</a></p></div>")
    txt = tips.text(t) + f"\n\nVibeCheck Weekly\n\nUnsubscribe: {u}\n"
    return h, txt, {"List-Unsubscribe": f"<{u}>", "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"}

def main():
    a = argparse.ArgumentParser(); a.add_argument("--date", default=tips._today()); a.add_argument("--dry-run", action="store_true"); o = a.parse_args()
    if not config.EMAIL_API_KEY: sys.exit("RESEND_API_KEY not set")
    if not config.CRON_SECRET: sys.exit("CRON_SECRET not set (needed for valid unsubscribe links); use the same value as on Render")
    t = next((x for x in tips.load() if x["date"] == o.date and x.get("status") == "published"), None)
    if not t: sys.exit(f"no published tip dated {o.date} in lib/tips.json")
    lock = open(LOG + ".lock", "w"); fcntl.flock(lock, fcntl.LOCK_EX)
    if already_sent(o.date): sys.exit(f"already sent for {o.date} (see {LOG}); not sending again")
    s, r = http.request("GET", f"{config.BASE_URL}/api/cron/unsub-sync", None, {"Authorization": f"Bearer {config.CRON_SECRET}"})
    if s != 200: sys.exit(f"unsubscribe sync failed ({s} {r}); not sending")
    blocked = set(r.get("unsubscribed", []))
    contacts = crm.list_contacts()
    to = sorted({c["email"].lower() for c in contacts if not c.get("unsubscribed")} - blocked)
    print(f"{len(contacts)} contacts, {len(to)} to send, {len(contacts) - len(to)} skipped (unsubscribed)")
    if o.dry_run:
        h, txt, hd = build(t, to[0] if to else "example@example.com"); print(t["subject"], "\n", txt, "\n", hd); return
    sent = failed = 0
    for e in to:
        h, txt, hd = build(t, e)
        st, rr = http.request("POST", (config.EMAIL_API_BASE or "https://api.resend.com") + "/emails",
            {"from": FROM, "reply_to": REPLY_TO, "to": [e], "subject": t["subject"], "html": h, "text": txt, "headers": hd},
            {"Authorization": f"Bearer {config.EMAIL_API_KEY}", "Idempotency-Key": f"daily-{o.date}-{e}"})
        if st < 300: sent += 1
        else: failed += 1; print("failed", e, st, rr)
    log(dict(date=o.date, slug=t["slug"], subject=t["subject"], status="sent" if sent else "failed", recipients=len(to), sent=sent, failed=failed, skipped_unsubscribed=len(contacts) - len(to)))
    print(f"sent={sent} failed={failed}; logged to {LOG}")
if __name__ == "__main__": main()
