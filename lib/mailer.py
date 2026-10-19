"""Transactional email via Resend or Postmark, chosen by EMAIL_PROVIDER. 'log' prints instead of sending."""
from . import config, http
def send(to, subject, html, text=None):
    p = config.EMAIL_PROVIDER
    if p == "resend" and config.EMAIL_API_KEY:
        s, r = http.request("POST", (config.EMAIL_API_BASE or "https://api.resend.com") + "/emails",
            {"from": config.EMAIL_FROM, "to": [to], "subject": subject, "html": html, "text": text or ""},
            {"Authorization": f"Bearer {config.EMAIL_API_KEY}"}); return s < 300
    if p == "postmark" and config.EMAIL_API_KEY:
        s, r = http.request("POST", (config.EMAIL_API_BASE or "https://api.postmarkapp.com") + "/email",
            {"From": config.EMAIL_FROM, "To": to, "Subject": subject, "HtmlBody": html, "TextBody": text or "", "MessageStream": "outbound"},
            {"X-Postmark-Server-Token": config.EMAIL_API_KEY, "Accept": "application/json"}); return s < 300
    print(f"[mail:log] to={to} subject={subject!r}"); return True
