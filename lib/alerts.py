"""Owner alerts for payments/cancellations. Recipient comes only from OWNER_ALERT_EMAIL; unset = no alerts.
Never raises: webhook handling must not depend on email delivery."""
import os, html, datetime
from zoneinfo import ZoneInfo
from . import db, mailer, config
PLAN_NAMES = {"solo": "Solo $19/mo", "pro": "Pro $49/mo"}
def _money(c, cur="usd"): return f"${(c or 0)/100:,.2f}" + ("" if (cur or "usd").lower() == "usd" else f" {cur.upper()}")
def _ct(ts): return datetime.datetime.fromtimestamp(ts or db.now(), ZoneInfo("America/Chicago")).strftime("%b %d, %Y %I:%M %p CT")
def _plan_for_price(pid):
    return pid and {config.STRIPE_PRICE_SOLO: "solo", config.STRIPE_PRICE_PRO: "pro"}.get(pid)
def _site_for(md, customer=None, sub=None):
    try:
        if md.get("scan_token"):
            r = db.one("SELECT url FROM scans WHERE token=?", (md["scan_token"],)); return r and r["url"]
        if md.get("site_key"):
            r = db.one("SELECT url FROM sites WHERE manage_key=?", (md["site_key"],)); return r and r["url"]
        if md.get("site_id"):
            r = db.one("SELECT url FROM sites WHERE id=?", (int(md["site_id"]),)); return r and r["url"]
        acc = db.one("SELECT id FROM accounts WHERE stripe_subscription=? OR stripe_customer=?", (sub or "-", customer or "-"))
        if acc:
            r = db.one("SELECT url FROM sites WHERE account_id=? ORDER BY weekly DESC, id LIMIT 1", (acc["id"],)); return r and r["url"]
    except Exception: pass
    return None
def build(ev):
    t, o = ev.get("type"), (ev.get("data") or {}).get("object") or {}
    md = o.get("metadata") or {}
    if t == "checkout.session.completed":
        if o.get("payment_status") not in ("paid", "no_payment_required"): return None
        email = (o.get("customer_details") or {}).get("email") or o.get("customer_email")
        if md.get("kind") == "unlock": subj, what = "New sale: $9 report unlock", "Full report unlock ($9 one-time)"
        else:
            p = PLAN_NAMES.get(md.get("plan", "solo"), md.get("plan")); subj, what = f"New subscriber: {p}", f"Subscription: {p}"
        return subj, what, _money(o.get("amount_total"), o.get("currency")), email, _site_for(md, o.get("customer"), o.get("subscription"))
    if t == "invoice.paid":
        sub = o.get("subscription") or (((o.get("parent") or {}).get("subscription_details") or {}).get("subscription"))
        # Only true renewals. One-time payments (Managed Payments invoices) and first invoices are covered by the checkout alert.
        if not sub or o.get("billing_reason") != "subscription_cycle" or not o.get("amount_paid"): return None
        line = ((o.get("lines") or {}).get("data") or [{}])[0]
        pid = (line.get("price") or {}).get("id") or ((line.get("pricing") or {}).get("price_details") or {}).get("price")
        p = PLAN_NAMES.get(_plan_for_price(pid), "subscription")
        return f"Renewal: {p}", f"Subscription renewal: {p}", _money(o.get("amount_paid"), o.get("currency")), o.get("customer_email"), _site_for({}, o.get("customer"), sub)
    if t == "charge.refunded":
        if not md.get("scan_token") and o.get("payment_intent") and config.STRIPE_SECRET_KEY:
            try:
                from . import http
                st, r = http.request("GET", config.STRIPE_API_BASE + "/v1/checkout/sessions?payment_intent=" + o["payment_intent"], None, {"Authorization": f"Bearer {config.STRIPE_SECRET_KEY}"})
                if st == 200 and r.get("data"): md = r["data"][0].get("metadata") or {}
            except Exception: pass
        return "Cancelled: refund issued", "Refund", "-" + _money(o.get("amount_refunded"), o.get("currency")), (o.get("billing_details") or {}).get("email") or o.get("receipt_email"), _site_for(md, o.get("customer"))
    if t == "customer.subscription.deleted":
        item = ((o.get("items") or {}).get("data") or [{}])[0]
        p = PLAN_NAMES.get(_plan_for_price((item.get("price") or {}).get("id")), "subscription")
        acc = db.one("SELECT email FROM accounts WHERE stripe_subscription=?", (o.get("id"),))
        return f"Cancelled: {p}", f"Subscription ended: {p}", "$0.00 (no further charges)", acc and acc["email"], _site_for({}, o.get("customer"), o.get("id"))
    return None
def send_alert(subj, what, amount, email, site, when, to=None, test=False):
    to = to or os.environ.get("OWNER_ALERT_EMAIL")
    if not to: return False
    if test: subj = "[TEST] " + subj
    rows = [("What", what), ("Amount charged (incl. tax)", amount), ("Customer email", email or "unknown"), ("App/site scanned", site or "unknown"), ("Time", when)]
    text = "\n".join(f"{k}: {v}" for k, v in rows)
    body = "<p>" + "<br>".join(f"<b>{html.escape(k)}:</b> {html.escape(str(v))}" for k, v in rows) + "</p>"
    return mailer.send(to, subj, body, text)
def notify(ev):
    try:
        if not os.environ.get("OWNER_ALERT_EMAIL"): return
        info = build(ev)
        if not info: return
        eid = ev.get("id") or ""
        if not eid or db.one("SELECT event_id FROM owner_alerts WHERE event_id=?", (eid,)): return
        try: db.q("INSERT INTO owner_alerts(event_id, created_at) VALUES(?, ?)", (eid, db.now()))
        except Exception: return  # concurrent retry already claimed it
        send_alert(*info, _ct(ev.get("created")))
    except Exception as e:
        print(f"[alerts] failed: {type(e).__name__}: {e}")
