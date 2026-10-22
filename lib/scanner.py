"""Passive scanner: fetches only publicly served pages/assets of a submitted URL."""
import re, time, ssl, socket, ipaddress, urllib.request, urllib.parse, html, os
UA = "VibeCheckWeeklyBot/0.1 (+owner-requested passive scan)"
MAX_BYTES = 3_000_000
MAX_SCRIPTS = 12

SECRET_PATTERNS = [
    ("OpenAI API key", r"sk-(?:proj-|svcacct-)?[A-Za-z0-9_\-]{32,}", "critical"),
    ("Stripe secret key", r"sk_live_[A-Za-z0-9]{20,}", "critical"),
    ("Stripe restricted key", r"rk_live_[A-Za-z0-9]{20,}", "critical"),
    ("AWS access key ID", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b", "critical"),
    ("Anthropic API key", r"sk-ant-[A-Za-z0-9_\-]{30,}", "critical"),
    ("Google API key", r"AIza[0-9A-Za-z_\-]{35}", "warning"),
    ("GitHub token", r"\bgh[pousr]_[A-Za-z0-9]{36,}\b", "critical"),
    ("Private key block", r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----", "critical"),
]
JWT_RE = re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}")
SUPA_URL_RE = re.compile(r"https://[a-z0-9]{15,30}\.supabase\.co")
SEC_HEADERS = {
    "strict-transport-security": "Forces browsers to always use HTTPS.",
    "content-security-policy": "Limits which scripts can run, reducing XSS damage.",
    "x-frame-options": "Stops other sites from embedding yours in a frame (clickjacking).",
    "x-content-type-options": "Stops browsers guessing file types.",
    "referrer-policy": "Controls how much URL info leaks to other sites.",
}

def is_public_host(host):
    if os.environ.get("ALLOW_PRIVATE_TARGETS") == "1": return True
    try: infos = socket.getaddrinfo(host, None)
    except Exception: return False
    for i in infos:
        ip = ipaddress.ip_address(i[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast or ip.is_unspecified: return False
    return True

class _Redir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, hdrs, newurl):
        if not is_public_host(urllib.parse.urlparse(newurl).hostname or ""): raise urllib.error.URLError("redirect to private address blocked")
        return super().redirect_request(req, fp, code, msg, hdrs, newurl)
_opener = urllib.request.build_opener(_Redir, urllib.request.HTTPSHandler(context=ssl.create_default_context()))

def fetch(url, limit=MAX_BYTES, timeout=15):
    if not is_public_host(urllib.parse.urlparse(url).hostname or ""): raise urllib.error.URLError("private address blocked")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    t = time.time()
    with _opener.open(req, timeout=timeout) as r:
        body = r.read(limit)
        return r.status, {k.lower(): v for k, v in r.headers.items()}, body.decode("utf-8", "replace"), time.time() - t, r.geturl()

def mask(s): return s[:8] + "…" + s[-4:]

def decode_jwt_role(tok):
    import base64, json
    try:
        p = tok.split(".")[1]; p += "=" * (-len(p) % 4)
        return json.loads(base64.urlsafe_b64decode(p)).get("role")
    except Exception: return None

def scan(url):
    f = []  # findings: dict(area, severity, title, detail, fix)
    def add(area, sev, title, detail, fix=None): f.append(dict(area=area, severity=sev, title=title, detail=detail, fix=fix))
    meta = {"url": url}
    try:
        status, headers, page, secs, final = fetch(url)
    except Exception as e:
        code = getattr(e, "code", None)
        if code in (401, 403, 429):
            add("Basics", "warning", "Your site's bot protection blocked our scanner", f"The server answered HTTP {code}. Many hosts (e.g. Cloudflare) block automated visitors. Allow the user agent '{UA}' or temporarily relax bot protection, then rescan.", None)
        else:
            add("Basics", "critical", "Site could not be reached", str(e)[:200], None)
        return dict(meta=meta, findings=f, score=0)
    meta.update(status=status, final_url=final, load_seconds=round(secs, 2), html_kb=round(len(page)/1024, 1))
    p = urllib.parse.urlparse(final); origin = f"{p.scheme}://{p.netloc}"

    # HTTPS
    if p.scheme != "https":
        add("Security", "critical", "Site is not served over HTTPS", f"Final URL is {final}.", "Configure my hosting so the site is only served over HTTPS and http:// requests redirect to https://.")
    else:
        add("Security", "pass", "HTTPS is on", "The site loads over an encrypted connection.")
        try:
            hs, _, _, _, hf = fetch("http://" + p.netloc, 1000, timeout=5)
            if not hf.startswith("https://"):
                add("Security", "warning", "HTTP does not redirect to HTTPS", "Visiting http:// does not send visitors to the secure version.", "Add a permanent (301) redirect from http:// to https:// for every page on my site.")
        except Exception: pass

    # headers
    missing = [h for h in SEC_HEADERS if h not in headers]
    for h in SEC_HEADERS:
        if h in headers: continue
        add("Security", "warning" if h in ("strict-transport-security", "content-security-policy") else "info",
            f"Missing security header: {h}", SEC_HEADERS[h], None)
    if missing:
        f.append(dict(area="Security", severity="fix", title="Fix prompt for security headers", detail="",
            fix="Add these HTTP response headers to every response from my site, using my host's config (e.g. vercel.json, netlify _headers, or middleware): " + ", ".join(missing) + ". Use a Content-Security-Policy that still allows my current scripts, fonts and Supabase/API domains, and explain each header you add."))

    # scripts
    srcs = re.findall(r"<script[^>]+src=[\"']([^\"']+)[\"']", page, re.I)
    srcs = [urllib.parse.urljoin(final, s) for s in srcs]
    base = ".".join((p.hostname or "").split(".")[-2:])
    same = [s for s in srcs if (urllib.parse.urlparse(s).hostname or "") == base or (urllib.parse.urlparse(s).hostname or "").endswith("." + base)][:MAX_SCRIPTS]
    blobs = [("page HTML", page)]
    for s in same:
        try: blobs.append((s.replace(origin, ""), fetch(s)[2]))
        except Exception: pass
    meta["scripts_checked"] = len(blobs) - 1
    found_secret = False
    for name, text in blobs:
        for label, pat, sev in SECRET_PATTERNS:
            for m in set(re.findall(pat, text))[:3] if False else list(dict.fromkeys(re.findall(pat, text)))[:3]:
                found_secret = True
                add("Security", sev, f"Possible {label} exposed in public code", f"Found {mask(m)} in {name}. Anyone visiting your site can read this.",
                    f"My site's public JavaScript contains a {label} ({mask(m)}). Move every secret key out of frontend code into server-side environment variables (e.g. a Supabase Edge Function or API route) and call that from the browser instead. Then tell me to rotate (revoke and re-create) this key in the provider dashboard, because it has already been exposed.")
        for tok in list(dict.fromkeys(JWT_RE.findall(text)))[:5]:
            role = decode_jwt_role(tok)
            if role == "service_role":
                found_secret = True
                add("Security", "critical", "Supabase service_role key exposed", f"Found {mask(tok)} in {name}. This key bypasses all database security rules.",
                    "My frontend contains the Supabase service_role key. Remove it from all client code, use only the anon/publishable key in the browser, move any admin operations to a Supabase Edge Function that reads the service key from secrets, and remind me to rotate the service_role key in Supabase settings.")
            elif role == "anon":
                add("Supabase", "info", "Supabase anon key in use", f"Found an anon key in {name}. This is normal, but it means your database is only as safe as your Row Level Security (RLS) rules.",
                    "My app uses Supabase with the anon key in the browser. List every table in my public schema, confirm Row Level Security is enabled on each one, and write policies so users can only read and write their own rows. Show me any table that is currently readable without login.")
        if SUPA_URL_RE.search(text) and not any(x["area"] == "Supabase" for x in f):
            add("Supabase", "info", "Supabase project detected", f"Your Supabase project URL appears in {name}. Make sure RLS is on for every table.", None)
    if not found_secret:
        add("Security", "pass", "No secret keys found in public code", f"Checked the page and {meta['scripts_checked']} script file(s) for common secret key patterns.")

    # SEO
    def tag(rx):
        m = re.search(rx, page, re.I | re.S); return html.unescape(m.group(1).strip()) if m else None
    title = tag(r"<title[^>]*>(.*?)</title>")
    desc = tag(r"<meta[^>]+name=[\"']description[\"'][^>]+content=[\"']([^\"']*)") or tag(r"<meta[^>]+content=[\"']([^\"']*)[\"'][^>]+name=[\"']description")
    og = re.findall(r"property=[\"'](og:[a-z]+)", page, re.I)
    if not title: add("Google visibility", "warning", "No page title", "Google uses the title as the blue link in results.", "Give every page a unique <title> under 60 characters that says what the page is and includes its main keyword.")
    else: add("Google visibility", "pass" if 10 <= len(title) <= 65 else "info", "Page title", f"\"{title[:80]}\" ({len(title)} characters; aim for 10–60).")
    if not desc: add("Google visibility", "warning", "No meta description", "Google often shows this text under your link.", "Add a unique meta description (120–160 characters) to every page that explains what the page offers and why to click.")
    else: add("Google visibility", "pass", "Meta description present", f"{len(desc)} characters.")
    need = {"og:title", "og:description", "og:image"} - {o.lower() for o in og}
    if need: add("Google visibility", "info", "Missing social preview tags", "Missing: " + ", ".join(sorted(need)) + ". Links shared on X, Slack, etc. will look bare.", "Add Open Graph and Twitter card meta tags (og:title, og:description, og:image at 1200x630, twitter:card=summary_large_image) to every public page.")
    else: add("Google visibility", "pass", "Social preview tags present", "og:title, og:description and og:image found.")
    text_len = len(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>", "", page, flags=re.S | re.I)).split())
    if text_len < 50:
        add("Google visibility", "warning", "Page has almost no readable text without JavaScript", f"Only about {text_len} words are in the raw HTML. Google may see a mostly empty page.", "My site is a client-side single-page app, so search engines see an almost empty HTML page. Add prerendering or static generation for my public pages (landing, pricing, blog) so their full text is in the initial HTML.")
    for path, label in (("/robots.txt", "robots.txt"), ("/sitemap.xml", "sitemap.xml")):
        try:
            s, h, b, _, _ = fetch(origin + path, 200_000)
            ok = s == 200 and "<html" not in b[:500].lower()
        except Exception: ok = False
        if ok: add("Google visibility", "pass", f"{label} found", "")
        else: add("Google visibility", "warning", f"No {label}", f"{origin}{path} is missing (or returns your app page instead).",
                  f"Create a {label} at the root of my site" + (" that allows all crawlers and points to my sitemap." if label == "robots.txt" else " listing every public page URL, and regenerate it whenever pages change. Then tell me how to submit it in Google Search Console."))
        if label == "robots.txt" and ok and re.search(r"(?im)^disallow:\s*/\s*$", b):
            add("Google visibility", "critical", "robots.txt blocks all crawlers", "Your robots.txt says Disallow: / — Google will not index your site.", "Change my robots.txt so it allows search engines to crawl my public pages.")

    # leftover noindex (meta robots / googlebot, X-Robots-Tag header)
    ni = []
    for m in re.finditer(r"<meta\b[^>]*>", page, re.I):
        t = m.group(0)
        nm = re.search(r"name\s*=\s*[\"']?\s*(robots|googlebot)\b", t, re.I)
        ct = re.search(r"content\s*=\s*[\"']([^\"']*)", t, re.I)
        if nm and ct and re.search(r"\b(noindex|none)\b", ct.group(1), re.I):
            ni.append(f'<meta name="{nm.group(1).lower()}" content="{ct.group(1).strip()}">')
    xr = headers.get("x-robots-tag", "")
    for part in re.split(r",(?=\s*[a-z0-9_-]+\s*:)", xr, flags=re.I) if xr else []:
        bot = re.match(r"\s*([a-z0-9_-]+)\s*:", part, re.I)
        if bot and bot.group(1).lower() not in ("googlebot", "all") and not re.match(r"\s*(unavailable_after|max-)", part, re.I): continue
        if re.search(r"\b(noindex|none)\b", part, re.I): ni.append(f"X-Robots-Tag: {xr.strip()[:100]} (response header)"); break
        ni.append(f"X-Robots-Tag: {xr.strip()[:100]} (response header)")
    if ni:
        add("Google visibility", "critical", "A noindex tag is telling Google not to list this page",
            "Found: " + "; ".join(ni) + ". Google will drop this page from search results. This is often left over from development.",
            "My live site tells Google not to index it (" + "; ".join(ni) + "). Remove the noindex robots/googlebot meta tag and any X-Robots-Tag: noindex header from my public pages (check my HTML head, SEO component, framework config and host settings such as vercel.json or _headers). Keep noindex only on private pages like admin or dashboards. Then tell me how to request indexing in Google Search Console.")
    else:
        add("Google visibility", "pass", "No noindex tag", "The page does not tell Google to stay away (checked robots/googlebot meta tags and the X-Robots-Tag header).")

    # speed
    sev = "pass" if secs < 1.0 else "info" if secs < 2.5 else "warning"
    add("Speed", sev, "Server response time", f"Main page downloaded in {secs:.2f}s ({meta['html_kb']} KB of HTML, {len(srcs)} script tags).",
        None if sev == "pass" else "My site's first load is slow. Enable caching/CDN for static assets, compress responses, and lazy-load anything not needed for the first screen.")

    pen = {"critical": 25, "warning": 8, "info": 2}
    score = max(0, 100 - sum(pen.get(x["severity"], 0) for x in f))
    return dict(meta=meta, findings=f, score=score)
