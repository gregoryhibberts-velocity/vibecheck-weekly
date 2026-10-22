"""Unit test for the leftover-noindex check. Run: ALLOW_PRIVATE_TARGETS=1 python3 tests/test_noindex.py"""
import os, sys, threading, http.server
os.environ.setdefault("ALLOW_PRIVATE_TARGETS", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import scanner
CASES = {
 "/meta": ('<meta name="robots" content="noindex, nofollow">', None, True),
 "/gbot": ("<meta content='NOINDEX' name='googlebot'>", None, True),
 "/hdr": ("", "noindex", True),
 "/hdrg": ("", "googlebot: noindex", True),
 "/other": ("", "bingbot: noindex", False),
 "/clean": ('<meta name="robots" content="index, follow">', None, False),
}
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        m, x, _ = CASES.get(self.path, ("", None, False))
        self.send_response(200); self.send_header("Content-Type", "text/html")
        if x: self.send_header("X-Robots-Tag", x)
        self.end_headers(); self.wfile.write(f"<html><head><title>Test page here</title>{m}</head><body>hi</body></html>".encode())
srv = http.server.HTTPServer(("127.0.0.1", 0), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
bad = 0
for path, (_, _, want) in CASES.items():
    r = scanner.scan(f"http://127.0.0.1:{srv.server_port}{path}")
    got = any(f["title"].startswith("A noindex tag") for f in r["findings"])
    print(path, "flagged" if got else "clean", "OK" if got == want else "FAIL"); bad += got != want
sys.exit(bad)
