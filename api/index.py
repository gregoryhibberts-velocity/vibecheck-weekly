"""Single Vercel Python serverless function; vercel.json rewrites every path here."""
import json, os, re, secrets, sys, urllib.parse
from http.server import BaseHTTPRequestHandler
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lib import config, db, scanner, verify, ratelimit, crm, mailer, billing, views, nudges, guides, tips

EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]+\.[^@\s]{2,}$")

def run_scan(site=None, url=None, email=None, unlocked=0):
    url = url or site["url"]
    if site and email is None:
        acc = db.one("SELECT * FROM accounts WHERE id=?", (site["account_id"],))
        email, unlocked = acc["email"], int(acc["plan"] != "free")
    r = scanner.scan(url)
    tok = secrets.token_urlsafe(12)
    db.insert("INSERT INTO scans(token, site_id, url, email, unlocked, status, score, result, created_at) VALUES(?,?,?,?,?,?,?,?,?)",
              (tok, site["id"] if site else None, url, email, unlocked, "done", r["score"], json.dumps(r), db.now()))
    return db.one("SELECT * FROM scans WHERE token=?", (tok,))

def email_report(site, scan, prev=None):
    if not scan.get("email"): return
    subj, h, t = views.report_email(site, scan, prev)
    mailer.send(scan["email"], subj, h, t)

def upsert_account(email):
    acc = db.one("SELECT * FROM accounts WHERE email=?", (email,))
    if acc: return acc, False
    db.insert("INSERT INTO accounts(email, created_at) VALUES(?,?)", (email, db.now()))
    return db.one("SELECT * FROM accounts WHERE email=?", (email,)), True

def new_verify_token(clean):
    t = os.environ.get("TEST_VERIFY_TOKEN", "").strip()
    if t and clean.startswith(config.BASE_URL.rstrip("/") + "/testsite"): return t
    return "vcw-" + secrets.token_hex(12)

def upsert_site(acc, url):
    u = urllib.parse.urlparse(url); host = u.hostname.lower(); clean = f"{u.scheme}://{u.netloc}{u.path or '/'}"
    s = db.one("SELECT * FROM sites WHERE account_id=? AND host=?", (acc["id"], host))
    if not s:
        db.insert("INSERT INTO sites(account_id, url, host, verify_token, manage_key, created_at) VALUES(?,?,?,?,?,?)",
                  (acc["id"], clean, host, new_verify_token(clean), secrets.token_urlsafe(18), db.now()))
        s = db.one("SELECT * FROM sites WHERE account_id=? AND host=?", (acc["id"], host))
    return s

def scan_mode(sc): return "full" if sc["unlocked"] else ("titles" if sc["email"] else "teaser")

def weekly_run(limit=20):
    """Called by Vercel Cron. Re-verifies ownership, rescans, emails. Batches to fit function time limits."""
    sites = db.all("""SELECT s.* FROM sites s WHERE s.weekly=1 AND s.verified_at IS NOT NULL AND
        COALESCE((SELECT MAX(created_at) FROM scans WHERE site_id=s.id),0) < ? ORDER BY s.id LIMIT ?""", (db.now() - 6*86400, limit))
    done = []
    for s in sites:
        origin = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(s["url"]))
        ok, _ = verify.check(s["url"], origin, s["verify_token"])
        if not ok:
            db.q("UPDATE sites SET weekly=0, verified_at=NULL WHERE id=?", (s["id"],))
            acc = db.one("SELECT email FROM accounts WHERE id=?", (s["account_id"],))
            mailer.send(acc["email"], f"{config.APP_NAME}: verification tag missing on {s['host']}",
                        f"<p>We couldn't find your verification tag on {s['host']}, so weekly checks are paused. Re-add it and verify again at {config.BASE_URL}/site/{s['manage_key']}</p>")
            done.append({"site": s["host"], "status": "paused-unverified"}); continue
        prev = db.one("SELECT score FROM scans WHERE site_id=? ORDER BY created_at DESC LIMIT 1", (s["id"],))
        sc = run_scan(s); email_report(s, sc, prev["score"] if prev else None)
        done.append({"site": s["host"], "status": "scanned", "score": sc["score"]})
    return done

class handler(BaseHTTPRequestHandler):
    def _send(self, code, body="", ctype="text/html; charset=utf-8", headers=None):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(b)))
        for k, v in {"X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY", "Referrer-Policy": "same-origin",
                     "Strict-Transport-Security": "max-age=31536000", **(headers or {})}.items(): self.send_header(k, v)
        self.end_headers(); self.wfile.write(b)
    def _redirect(self, loc): self._send(303, "", headers={"Location": loc})
    def _json(self, code, obj): self._send(code, json.dumps(obj), "application/json")
    def _ip(self):
        return (self.headers.get("x-forwarded-for") or self.client_address[0]).split(",")[0].strip()
    def _body(self):
        n = min(int(self.headers.get("Content-Length") or 0), 1_000_000); return self.rfile.read(n)
    def _form(self): return {k: v[0] for k, v in urllib.parse.parse_qs(self._body().decode()).items()}
    def _site(self, key): return db.one("SELECT * FROM sites WHERE manage_key=?", (key,))

    def do_GET(self):
        p = urllib.parse.urlparse(self.path); path = p.path.rstrip("/") or "/"
        if path == "/": return self._send(200, views.landing())
        if path == "/testsite":
            t = os.environ.get("TEST_VERIFY_TOKEN", "").strip()
            if not t: return self._send(404, views.message("Not found", "Nothing here."))
            return self._send(200, f'<!doctype html><html><head><title>VibeCheck test site</title><meta name="vibecheck-verification" content="{t}"><meta name="robots" content="noindex"></head><body><h1>VibeCheck Weekly internal test site</h1><p>Used only for automated testing.</p></body></html>')
        if path == "/pricing": return self._send(200, views.pricing())
        if path == "/guides": return self._send(200, guides.index())
        if path.startswith("/guides/") and path[8:] in guides.GUIDES: return self._send(200, guides.render(path[8:]))
        if path == "/tips": return self._send(200, tips.index())
        if path == "/tips/rss.xml": return self._send(200, tips.rss(), "application/rss+xml; charset=utf-8")
        if path.startswith("/tips/"):
            h = tips.render(path[6:])
            if h: return self._send(200, h)
        if path == "/robots.txt": return self._send(200, f"User-agent: *\nAllow: /\nDisallow: /site/\nDisallow: /report/\nDisallow: /r/\nSitemap: {config.BASE_URL}/sitemap.xml\n", "text/plain")
        if path == "/sitemap.xml":
            return self._send(200, f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{config.BASE_URL}/</loc></url><url><loc>{config.BASE_URL}/pricing</loc></url><url><loc>{config.BASE_URL}/guides</loc></url>{"".join(f"<url><loc>{config.BASE_URL}/guides/{g}</loc></url>" for g in guides.GUIDES)}<url><loc>{config.BASE_URL}/tips</loc></url>{"".join(f"<url><loc>{tips.url(t)}</loc><lastmod>{t['date']}</lastmod></url>" for t in tips.published())}</urlset>', "application/xml")
        if path == "/api/health": return self._json(200, {"ok": True, "db": "postgres" if db.PG else "sqlite"})
        if path in ("/billing/success", "/billing/unlocked"):
            sid = urllib.parse.parse_qs(p.query).get("session_id", [""])[0]
            o = billing.get_session(sid)
            if o and o.get("status") == "complete": billing.apply_session(o)
            md = (o or {}).get("metadata") or {}
            if path == "/billing/unlocked" and md.get("scan_token"): return self._redirect(f"/r/{md['scan_token']}")
        if path == "/billing/success": return self._send(200, views.message("Payment received", "Thanks! Weekly monitoring turns on as soon as Stripe confirms the payment (usually seconds). Use your site link to check status."))
        if path == "/api/cron/weekly":
            if not config.CRON_SECRET or self.headers.get("Authorization") != f"Bearer {config.CRON_SECRET}": return self._json(401, {"error": "unauthorized"})
            return self._json(200, {"ran": weekly_run()})
        if path == "/api/cron/nudges":
            if not config.CRON_SECRET or self.headers.get("Authorization") != f"Bearer {config.CRON_SECRET}": return self._json(401, {"error": "unauthorized"})
            qs = urllib.parse.parse_qs(p.query); t = qs.get("test", [""])[0]
            if t: return self._json(200, {"test": nudges.send_tests(t, qs.get("report", [""])[0])})
            if qs.get("only", [""])[0] == "audience": return self._json(200, {"audience_added": nudges.sync_audience()})
            return self._json(200, nudges.run())
        if path == "/api/cron/unsub-sync":
            if not config.CRON_SECRET or self.headers.get("Authorization") != f"Bearer {config.CRON_SECRET}": return self._json(401, {"error": "unauthorized"})
            return self._json(200, nudges.sync_unsubscribes())
        if path == "/unsubscribe":
            qs = urllib.parse.parse_qs(p.query); e = qs.get("e", [""])[0].lower(); t = qs.get("t", [""])[0]
            if not nudges.check_unsub(e, t): return self._send(400, views.message("Link not valid", "This unsubscribe link is not valid."))
            nudges.do_unsubscribe(e)
            return self._send(200, views.message("Unsubscribed", "You will no longer receive emails from VibeCheck Weekly."))
        m = re.fullmatch(r"/site/([\w-]+)", path)
        if m:
            s = self._site(m.group(1))
            if not s: return self._send(404, views.message("Not found", "That site link is not valid."))
            return self._render_site(s)
        m = re.fullmatch(r"/r/([\w-]+)/monitor", path)
        if m: return self._report_action(m.group(1), "monitor")
        m = re.fullmatch(r"/(?:r|report)/([\w-]+)", path)
        if m:
            sc = db.one("SELECT * FROM scans WHERE token=?", (m.group(1),))
            if not sc: return self._send(404, views.message("Not found", "Report not found. Free reports are kept temporarily during our beta."))
            return self._send(200, views.report(sc, scan_mode(sc)))
        self._send(404, views.message("Not found", "Page not found."))

    def _render_site(self, s, err=None, code=200):
        acc = db.one("SELECT * FROM accounts WHERE id=?", (s["account_id"],))
        scans = db.all("SELECT token, score, created_at FROM scans WHERE site_id=? ORDER BY created_at DESC LIMIT 10", (s["id"],))
        wc = db.one("SELECT COUNT(*) AS n FROM sites WHERE account_id=? AND weekly=1", (acc["id"],))["n"]
        self._send(code, views.site_page(s, acc, scans, verify.instructions(s["verify_token"]), err, wc))

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path.rstrip("/")
        if path == "/api/stripe/webhook":
            raw = self._body()
            if not billing.verify_signature(raw, self.headers.get("Stripe-Signature", "")): return self._json(400, {"error": "bad signature"})
            return self._json(200, {"result": billing.handle_event(json.loads(raw))})
        if path == "/unsubscribe":
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query); e = qs.get("e", [""])[0].lower(); t = qs.get("t", [""])[0]
            if not nudges.check_unsub(e, t): return self._json(400, {"error": "invalid"})
            nudges.do_unsubscribe(e); return self._json(200, {"ok": True})
        if path == "/start": return self._start()
        if path == "/scan": return self._free_scan()
        m = re.fullmatch(r"/r/([\w-]+)/(email|unlock|monitor)", path)
        if m: return self._report_action(m.group(1), m.group(2))
        m = re.fullmatch(r"/site/([\w-]+)/(verify|scan|checkout|monitor)", path)
        if not m: return self._send(404, views.message("Not found", "Page not found."))
        s = self._site(m.group(1))
        if not s: return self._send(404, views.message("Not found", "That site link is not valid."))
        action = m.group(2); form = self._form()
        if action == "verify":
            origin = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(s["url"]))
            ok, how = verify.check(s["url"], origin, s["verify_token"])
            if not ok: return self._render_site(s, "We couldn't find the tag or file yet. Make sure you deployed the change, then try again.", 200)
            db.q("UPDATE sites SET verified_at=? WHERE id=?", (db.now(), s["id"])); s = self._site(s["manage_key"])
            action = "scan"
        if action == "scan":
            if not s["verified_at"]: return self._render_site(s, "Please verify ownership first.")
            acc = db.one("SELECT * FROM accounts WHERE id=?", (s["account_id"],))
            if not ratelimit.hit("scan-ip:" + self._ip(), config.RL_SCANS_PER_IP_HOUR, 3600) or \
               not ratelimit.hit("scan-email:" + acc["email"], config.RL_SCANS_PER_EMAIL_DAY, 86400):
                return self._send(429, views.message("Slow down", "You've hit the scan limit for now. Please try again later."))
            sc = run_scan(s); email_report(s, sc)
            return self._redirect(f"/r/{sc['token']}")
        acc = db.one("SELECT * FROM accounts WHERE id=?", (s["account_id"],))
        if action == "checkout":
            if not s["verified_at"]: return self._render_site(s, "Please verify ownership before upgrading.")
            plan = form.get("plan") if form.get("plan") in config.PLANS else "solo"
            url, err = billing.checkout_url(plan, acc, s["id"], s["manage_key"])
            return self._redirect(url) if url else self._send(503, views.message("Checkout unavailable", err))
        if action == "monitor":
            wc = db.one("SELECT COUNT(*) AS n FROM sites WHERE account_id=? AND weekly=1", (acc["id"],))["n"]
            if acc["plan"] != "pro" or wc >= config.PLANS["pro"]["apps"] or not s["verified_at"]:
                return self._render_site(s, "Your plan doesn't allow another monitored app.")
            db.q("UPDATE sites SET weekly=1 WHERE id=?", (s["id"],)); return self._redirect(f"/site/{s['manage_key']}")

    def _free_scan(self):
        f = self._form(); url = (f.get("url") or "").strip()
        if url and "://" not in url: url = "https://" + url
        u = urllib.parse.urlparse(url)
        if f.get("owner") != "1" or u.scheme not in ("http", "https") or not u.hostname:
            return self._send(400, views.message("Check your details", "Please enter a valid URL and confirm you own the app."))
        if not scanner.is_public_host(u.hostname): return self._send(400, views.message("Not allowed", "Private or internal addresses can't be checked."))
        if not ratelimit.hit("free-ip:" + self._ip(), config.RL_FREE_SCANS_PER_IP_DAY, 86400) or not ratelimit.hit("free-host:" + u.hostname.lower(), 20, 86400):
            return self._send(429, views.message("Slow down", "You've reached today's free check limit. Please try again tomorrow."))
        sc = run_scan(url=f"{u.scheme}://{u.netloc}{u.path or '/'}")
        return self._redirect(f"/r/{sc['token']}")

    def _report_action(self, tok, action):
        sc = db.one("SELECT * FROM scans WHERE token=?", (tok,))
        if not sc: return self._send(404, views.message("Not found", "Report not found."))
        f = self._form() if self.command == "POST" else {}
        if action == "email":
            email = (f.get("email") or "").strip().lower()
            if not EMAIL_RE.match(email): return self._send(400, views.message("Check your email", "Please enter a valid email address."))
            if not ratelimit.hit("start-email:" + email, 20, 86400): return self._send(429, views.message("Slow down", "Too many requests. Try later."))
            acc, new = upsert_account(email)
            db.q("UPDATE scans SET email=?, unlocked=CASE WHEN ?='free' THEN unlocked ELSE 1 END WHERE token=?", (email, acc["plan"], tok))
            if new and crm.add_signup(email): nudges._mark(email, 'audience')
            email_report(None, db.one("SELECT * FROM scans WHERE token=?", (tok,)))
            return self._redirect(f"/r/{tok}")
        if not sc["email"]: return self._redirect(f"/r/{tok}")
        if action == "unlock":
            if sc["unlocked"]: return self._redirect(f"/r/{tok}")
            url, err = billing.unlock_url(sc)
            return self._redirect(url) if url else self._send(503, views.message("Checkout unavailable", err))
        if action == "monitor":
            acc, _ = upsert_account(sc["email"]); s = upsert_site(acc, sc["url"])
            if s["id"] != sc["site_id"]: db.q("UPDATE scans SET site_id=? WHERE token=?", (s["id"], tok))
            return self._redirect(f"/site/{s['manage_key']}")

    def _start(self):
        f = self._form(); url = (f.get("url") or "").strip(); email = (f.get("email") or "").strip().lower()
        if "://" not in url and url: url = "https://" + url
        u = urllib.parse.urlparse(url)
        if f.get("owner") != "1" or u.scheme not in ("http", "https") or not u.hostname or not EMAIL_RE.match(email):
            return self._send(400, views.message("Check your details", "Please enter a valid URL and email, and confirm you own the app."))
        if not scanner.is_public_host(u.hostname): return self._send(400, views.message("Not allowed", "Private or internal addresses can't be checked."))
        if not ratelimit.hit("start-ip:" + self._ip(), 20, 3600) or not ratelimit.hit("start-email:" + email, 10, 86400):
            return self._send(429, views.message("Slow down", "Too many sign-ups from you recently. Please try again later."))
        acc = db.one("SELECT * FROM accounts WHERE email=?", (email,))
        new = acc is None
        if new: db.insert("INSERT INTO accounts(email, created_at) VALUES(?,?)", (email, db.now())); acc = db.one("SELECT * FROM accounts WHERE email=?", (email,))
        host = u.hostname.lower(); clean = f"{u.scheme}://{u.netloc}{u.path or '/'}"
        s = db.one("SELECT * FROM sites WHERE account_id=? AND host=?", (acc["id"], host))
        if not s:
            db.insert("INSERT INTO sites(account_id, url, host, verify_token, manage_key, created_at) VALUES(?,?,?,?,?,?)",
                      (acc["id"], clean, host, new_verify_token(clean), secrets.token_urlsafe(18), db.now()))
            s = db.one("SELECT * FROM sites WHERE account_id=? AND host=?", (acc["id"], host))
        if new and crm.add_signup(email): nudges._mark(email, 'audience')
        mailer.send(email, f"Verify {host} for your {config.APP_NAME} check",
                    f"<p>Your private link for {host}: <a href='{config.BASE_URL}/site/{s['manage_key']}'>{config.BASE_URL}/site/{s['manage_key']}</a></p>")
        return self._redirect(f"/site/{s['manage_key']}")
    def do_HEAD(self):
        real = self.wfile
        class _Null:
            def write(self, b): pass
        orig = self.end_headers
        def eh(): orig(); self.wfile = _Null()
        self.end_headers = eh
        try: self.do_GET()
        finally: self.wfile = real
    def log_message(self, *a): pass
