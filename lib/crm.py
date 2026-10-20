"""Resend Audience: add/remove sign-up contacts. No-op (logged) if not configured."""
import urllib.parse
from . import config, http
def _h(): return {"Authorization": f"Bearer {config.EMAIL_API_KEY}"}
def _base(): return (config.EMAIL_API_BASE or "https://api.resend.com") + f"/audiences/{config.RESEND_AUDIENCE_ID}/contacts"
def _ok(): return bool(config.EMAIL_API_KEY and config.RESEND_AUDIENCE_ID)
def add_signup(email):
    if not _ok(): print(f"[crm] audience not configured; skipped {email}"); return False
    s, r = http.request("POST", _base(), {"email": email, "unsubscribed": False}, _h())
    if s >= 300 and "already" not in str(r).lower(): print("[crm] add failed", s, r); return False
    return True
def unsubscribe(email):
    if not _ok(): return False
    s, r = http.request("PATCH", _base() + "/" + urllib.parse.quote(email), {"unsubscribed": True}, _h())
    if s == 404:  # not in the audience yet: add it as unsubscribed so it stays opted out
        s, r = http.request("POST", _base(), {"email": email, "unsubscribed": True}, _h())
    if s >= 300: print("[crm] unsubscribe failed", s, r)
    return s < 300
def list_contacts():
    s, r = http.request("GET", _base(), None, _h())
    if s >= 300: raise RuntimeError(f"[crm] list failed {s} {r}")
    return r.get("data", [])
