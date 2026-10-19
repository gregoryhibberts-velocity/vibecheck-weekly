"""Ownership check: a meta tag on the home page OR /.well-known/vibecheck-verify.txt containing the token."""
import re
from . import scanner
META_NAME = "vibecheck-verification"
def instructions(token):
    return {"meta": f'<meta name="{META_NAME}" content="{token}">', "file_path": "/.well-known/vibecheck-verify.txt", "file_body": token}
def check(url, host_origin, token):
    try:
        _, _, page, _, _ = scanner.fetch(url, 500_000, timeout=10)
        for m in re.finditer(r"<meta[^>]+>", page, re.I):
            tag = m.group(0)
            if META_NAME in tag and re.search(r'content=["\']' + re.escape(token) + r'["\']', tag): return True, "meta tag"
    except Exception: pass
    try:
        s, _, body, _, _ = scanner.fetch(host_origin + "/.well-known/vibecheck-verify.txt", 2000, timeout=10)
        if s == 200 and body.strip() == token: return True, "well-known file"
    except Exception: pass
    return False, None
