"""Stripe Checkout + webhook verification using Stripe's REST API directly (no SDK needed)."""
import hmac, hashlib, time
from . import config, http, db
AUTH = lambda: {"Authorization": f"Bearer {config.STRIPE_SECRET_KEY}"}
def _session(mode, price, email, customer, metadata, success, cancel):
    if not (config.STRIPE_SECRET_KEY and price): return None, "Payments are not configured yet."
    data = {"mode": mode, "line_items[0][price]": price, "line_items[0][quantity]": 1,
            "success_url": success, "cancel_url": cancel}
    for k, v in metadata.items(): data[f"metadata[{k}]"] = str(v)
    if customer: data["customer"] = customer
    elif email: data["customer_email"] = email
    s, r = http.request("POST", config.STRIPE_API_BASE + "/v1/checkout/sessions", data, AUTH(), form=True)
    return (r.get("url"), None) if s == 200 else (None, (r.get("error") or {}).get("message", "Stripe error"))
def checkout_url(plan, account, site_id, site_key=None):
    price = {"solo": config.STRIPE_PRICE_SOLO, "pro": config.STRIPE_PRICE_PRO}.get(plan)
    return _session("subscription", price, account["email"], account.get("stripe_customer"),
                    {"kind": "subscription", "plan": plan, "site_id": site_id, "account_id": account["id"], "site_key": site_key or ""},
                    f"{config.BASE_URL}/billing/success?session_id={{CHECKOUT_SESSION_ID}}", f"{config.BASE_URL}/pricing")
def unlock_url(scan):
    return _session("payment", config.STRIPE_PRICE_UNLOCK, scan["email"], None, {"kind": "unlock", "scan_token": scan["token"]},
                    f"{config.BASE_URL}/billing/unlocked?session_id={{CHECKOUT_SESSION_ID}}", f"{config.BASE_URL}/r/{scan['token']}")
def get_session(sid):
    if not config.STRIPE_SECRET_KEY or not sid.startswith("cs_"): return None
    s, r = http.request("GET", config.STRIPE_API_BASE + "/v1/checkout/sessions/" + sid, None, AUTH())
    return r if s == 200 else None
def verify_signature(payload: bytes, header: str, tolerance=300):
    if not (config.STRIPE_WEBHOOK_SECRET and header): return False
    parts = dict(p.split("=", 1) for p in header.split(",") if "=" in p)
    sigs = [p.split("=", 1)[1] for p in header.split(",") if p.startswith("v1=")]
    t = parts.get("t")
    if not t or abs(time.time() - int(t)) > tolerance: return False
    exp = hmac.new(config.STRIPE_WEBHOOK_SECRET.encode(), f"{t}.".encode() + payload, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(exp, s) for s in sigs)
def apply_session(o):
    """Idempotently apply a paid checkout session (from webhook or success-page lookup)."""
    md = o.get("metadata") or {}
    if md.get("kind") == "unlock":
        if o.get("payment_status") != "paid": return "unpaid"
        db.q("UPDATE scans SET unlocked=1 WHERE token=?", (md.get("scan_token"),)); return "unlocked"
    if md.get("site_key"):
        site = db.one("SELECT id, account_id FROM sites WHERE manage_key=?", (md["site_key"],))
        if site: md = {**md, "site_id": str(site["id"]), "account_id": str(site["account_id"])}
    aid = int(md.get("account_id") or o.get("client_reference_id") or 0)
    db.q("UPDATE accounts SET plan=?, stripe_customer=?, stripe_subscription=? WHERE id=?",
         (md.get("plan", "solo"), o.get("customer"), o.get("subscription"), aid))
    if md.get("site_id"): db.q("UPDATE sites SET weekly=1 WHERE id=? AND account_id=?", (int(md["site_id"]), aid))
    db.q("UPDATE scans SET unlocked=1 WHERE email=(SELECT email FROM accounts WHERE id=?)", (aid,))
    return "activated"
def handle_event(ev):
    t, o = ev.get("type"), ev.get("data", {}).get("object", {})
    if t == "checkout.session.completed": return apply_session(o)
    if t == "customer.subscription.deleted":
        acc = db.one("SELECT id FROM accounts WHERE stripe_subscription=?", (o.get("id"),))
        if acc:
            db.q("UPDATE accounts SET plan='free' WHERE id=?", (acc["id"],)); db.q("UPDATE sites SET weekly=0 WHERE account_id=?", (acc["id"],))
        return "cancelled"
    return "ignored"
