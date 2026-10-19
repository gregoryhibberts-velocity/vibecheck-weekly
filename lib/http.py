import json, urllib.request, urllib.parse
def request(method, url, data=None, headers=None, form=False, timeout=20):
    h = dict(headers or {})
    body = None
    if data is not None:
        if form: body = urllib.parse.urlencode(data, doseq=True).encode(); h.setdefault("Content-Type", "application/x-www-form-urlencoded")
        else: body = json.dumps(data).encode(); h.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r: return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read() or b"{}")
        except Exception: return e.code, {}
