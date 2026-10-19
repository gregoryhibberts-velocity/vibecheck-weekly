"""Render entry point: long-running Python server using the same request handler as the Vercel build."""
import os
from http.server import ThreadingHTTPServer
from api.index import handler
port = int(os.environ.get("PORT", 10000))
print(f"VibeCheck Weekly listening on :{port}", flush=True)
ThreadingHTTPServer(("0.0.0.0", port), handler).serve_forever()
