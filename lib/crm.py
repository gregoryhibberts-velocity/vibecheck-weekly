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
    s, _ = http.request("DELETE", _base() + "/" + urllib.parse.quote(email), None, _h())
    return s < 300 or s == 404
