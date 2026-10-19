"""ActiveCampaign: upsert contact and subscribe to list. No-op (logged) if env vars missing."""
from . import config, http
def add_signup(email, tags=None):
    if not (config.AC_API_URL and config.AC_API_KEY and config.AC_LIST_ID):
        print(f"[crm] ActiveCampaign not configured; skipped {email}"); return False
    base = config.AC_API_URL.rstrip("/") + "/api/3"
    h = {"Api-Token": config.AC_API_KEY}
    s, r = http.request("POST", base + "/contact/sync", {"contact": {"email": email}}, h)
    cid = (r.get("contact") or {}).get("id")
    if not cid: print("[crm] contact sync failed", s, r); return False
    s2, _ = http.request("POST", base + "/contactLists", {"contactList": {"list": int(config.AC_LIST_ID), "contact": int(cid), "status": 1}}, h)
    return s2 in (200, 201)
