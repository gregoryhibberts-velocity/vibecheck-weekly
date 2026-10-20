import json, os, re, time, hmac, hashlib, urllib.request, urllib.parse, http.client, subprocess
B = "http://127.0.0.1:3000"; FIX = os.path.join(os.path.dirname(__file__), "..", "fixture")
def req(method, path, data=None, headers=None, raw=None):
    c = http.client.HTTPConnection("127.0.0.1", 3000, timeout=90)
    body = raw if raw is not None else (urllib.parse.urlencode(data) if data else None)
    h = {"Content-Type": "application/x-www-form-urlencoded", **(headers or {})}
    c.request(method, path, body=body, headers=h); r = c.getresponse(); return r.status, r.getheader("Location"), r.read().decode()
results = []
def check(name, cond, info=""): results.append((name, bool(cond))); print(("PASS " if cond else "FAIL ") + name, info)

open(os.path.join(FIX, "index.html"), "w").write('<html><head><title>Fixture</title></head><body><div id=root></div><script src="/app.js"></script></body></html>')
s, loc, _ = req("POST", "/start", {"url": "https://example.com", "email": "a@b.co"}); check("start rejects missing ownership tick", s == 400)
s, loc, _ = req("POST", "/start", {"url": "http://127.0.0.1:8099/", "email": "Owner@Test.dev", "owner": "1"})
check("start creates site and redirects", s == 303 and loc.startswith("/site/"), loc); key = loc.split("/")[-1]
s, _, body = req("GET", loc); token = re.search(r"vcw-[0-9a-f]{24}", body).group(0); check("site page shows verify instructions", "vibecheck-verification" in body)
open("/workspace/appcheck/shots/_verify_url.txt", "w").write(loc)
s, loc2, body = req("POST", f"/site/{key}/scan"); check("scan blocked before verification", "verify ownership first" in body)
s, loc2, body = req("POST", f"/site/{key}/verify"); check("verify fails without tag", "find the tag or file yet" in body)
open(os.path.join(FIX, "index.html"), "w").write(f'<html><head><title>Fixture</title><meta name="vibecheck-verification" content="{token}"></head><body><div id=root></div><script src="/app.js"></script></body></html>')
s, loc2, _ = req("POST", f"/site/{key}/verify"); check("verify with meta tag runs scan", s == 303 and loc2.startswith("/r/"), loc2)
open("/workspace/appcheck/shots/_report_url.txt", "w").write(loc2)
s, _, body = req("GET", loc2); check("report shows service_role finding", "service_role key exposed" in body)
s, loc3, _ = req("POST", f"/site/{key}/checkout", {"plan": "pro"}); check("checkout redirects to Stripe", s == 303 and "checkout.stripe.com" in (loc3 or ""), loc3)
ev = json.dumps({"type": "checkout.session.completed", "data": {"object": {"customer": "cus_1", "subscription": "sub_1", "client_reference_id": "1", "metadata": {"plan": "pro", "site_id": "1", "account_id": "1"}}}})
t = str(int(time.time())); sig = hmac.new(os.environ["STRIPE_WEBHOOK_SECRET"].encode(), f"{t}.{ev}".encode(), hashlib.sha256).hexdigest()
s, _, body = req("POST", "/api/stripe/webhook", raw=ev, headers={"Stripe-Signature": f"t={t},v1=deadbeef", "Content-Type": "application/json"}); check("webhook rejects bad signature", s == 400)
s, _, body = req("POST", "/api/stripe/webhook", raw=ev, headers={"Stripe-Signature": f"t={t},v1={sig}", "Content-Type": "application/json"}); check("webhook activates plan", s == 200 and "activated" in body, body)
s, _, body = req("GET", f"/site/{key}"); check("site shows Pro + weekly on", "Pro" in body and "Weekly monitoring: <b>on" in body)
open("/workspace/appcheck/shots/_site_url.txt", "w").write(f"/site/{key}")
s, _, _ = req("GET", "/api/cron/weekly"); check("cron rejects without secret", s == 401)
s, _, body = req("GET", "/api/cron/weekly", headers={"Authorization": "Bearer " + os.environ["CRON_SECRET"]}); check("cron skips recently scanned", s == 200 and json.loads(body)["ran"] == [], body)
subprocess.run(["psql", "-h", "/tmp/pg", "-p", "55432", "-U", "vc", "-d", "vibecheck", "-qc", "UPDATE scans SET created_at = created_at - 7*86400"], check=True)
s, _, body = req("GET", "/api/cron/weekly", headers={"Authorization": "Bearer " + os.environ["CRON_SECRET"]}); check("cron rescans weekly site", '"scanned"' in body, body)
codes = [req("POST", f"/site/{key}/scan")[0] for _ in range(6)]; check("rate limit kicks in (per email 5/day)", 429 in codes, codes)
import xml.dom.minidom
s, _, body = req("GET", "/tips"); check("tips index", s == 200 and "/tips/" in body, s)
slug = json.load(open(os.path.join(os.path.dirname(__file__), "..", "lib", "tips.json")))[0]["slug"]
s, _, body = req("GET", "/tips/" + slug); check("tip page", s == 200, s)
s, _, body = req("GET", "/tips/no-such-tip"); check("unknown tip 404", s == 404, s)
s, _, body = req("GET", "/tips/rss.xml"); xml.dom.minidom.parseString(body); check("rss valid xml with item", s == 200 and "<item>" in body, s)
s, _, body = req("GET", "/sitemap.xml"); check("sitemap lists tips", "/tips/" + slug in body)
s, _, body = req("POST", "/unsubscribe?e=x%40example.com&t=bad", raw=b"List-Unsubscribe=One-Click"); check("one-click unsubscribe rejects bad token", s == 400, s)
tok = hmac.new(("unsub:" + os.environ["CRON_SECRET"]).encode(), b"u@example.com", hashlib.sha256).hexdigest()[:32]
s, _, body = req("POST", f"/unsubscribe?e=u%40example.com&t={tok}", raw=b"List-Unsubscribe=One-Click"); check("one-click unsubscribe ok", s == 200, s)
s, _, body = req("GET", "/api/cron/unsub-sync", headers={"Authorization": "Bearer " + os.environ["CRON_SECRET"]}); d = json.loads(body)
check("unsub sync merges local + Resend", "u@example.com" in d["unsubscribed"] and "gone@example.com" in d["unsubscribed"], body)
calls = [json.loads(l) for l in open(os.path.join(os.path.dirname(__file__), "mock_calls.jsonl"))]
check("Resend contact PATCHed unsubscribed=true", any(c.get("method") == "PATCH" and "u%40example.com" in c["path"] and '"unsubscribed": true' in c["body"] for c in calls))
calls = [json.loads(l) for l in open(os.path.join(os.path.dirname(__file__), "mock_calls.jsonl"))]
paths = [c["path"] for c in calls]
check("Resend audience contact added", any(x.startswith("/audiences/aud_mock/contacts") for x in paths))
check("Stripe checkout session created with auth", any(c["path"] == "/v1/checkout/sessions" and c["auth_present"] for c in calls))
check("transactional emails sent", paths.count("/emails") >= 3, paths.count("/emails"))
print(f"\n{sum(ok for _, ok in results)}/{len(results)} checks passed")
