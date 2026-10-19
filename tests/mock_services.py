"""Fake Stripe / ActiveCampaign / Resend APIs for local end-to-end tests. Logs every call to tests/mock_calls.jsonl."""
import json, os
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
LOG = os.path.join(os.path.dirname(__file__), "mock_calls.jsonl")
class H(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode()
        auth = self.headers.get("Authorization") or self.headers.get("Api-Token") or ""
        with open(LOG, "a") as f: f.write(json.dumps({"path": self.path, "auth_present": bool(auth), "body": body[:500]}) + "\n")
        if self.path == "/v1/checkout/sessions": r = {"id": "cs_test_123", "url": "https://checkout.stripe.com/c/pay/cs_test_123"}
        elif self.path == "/ac/api/3/contact/sync": r = {"contact": {"id": "42"}}
        elif self.path == "/ac/api/3/contactLists": r = {"contactList": {"id": "7"}}
        elif self.path == "/emails": r = {"id": "email_1"}
        else: self.send_response(404); self.end_headers(); return
        b = json.dumps(r).encode(); self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass
if __name__ == "__main__": ThreadingHTTPServer(("127.0.0.1", 4010), H).serve_forever()
