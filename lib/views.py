import html, json, time, urllib.parse
from . import config
E = html.escape
CSS = """html{background:#fff}body{min-height:100vh;font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:0;background:#fff linear-gradient(180deg,#eef3ff 0%,#f8fafd 420px,#ffffff 100%) no-repeat;color:#1f2937}
a{color:#1d4ed8}.wrap{max-width:860px;margin:0 auto;padding:40px 24px}h1{font-size:40px;margin:.2em 0}
.sub{color:#4b5563;font-size:19px;line-height:1.5}.card{background:#fff;border:1px solid #e3e8f0;box-shadow:0 1px 3px rgba(16,24,40,.04);border-radius:14px;padding:24px;margin:22px 0}
input[type=url],input[name=url],input[type=email]{width:100%;box-sizing:border-box;padding:13px;margin:6px 0 14px;border-radius:8px;border:1px solid #cfd6e3;background:#fff;color:#1f2937;font-size:16px}
button{background:#2563eb;color:#fff;border:0;border-radius:8px;padding:13px 20px;font-size:16px;cursor:pointer}button.alt{background:#6d28d9}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.grid div{background:#fff;border:1px solid #e3e8f0;border-radius:12px;padding:16px;color:#374151}.grid div div{background:none;border:0;padding:0;border-radius:0}
.f{border:1px solid #e3e8f0;border-left:5px solid #9ca3af;padding:12px 16px;margin:10px 0;background:#fff;border-radius:8px}
.critical{border-left-color:#dc2626}.warning{border-left-color:#d97706}.info{border-left-color:#3b82f6}.pass{border-left-color:#16a34a}.fix{border-left-color:#7c3aed}
.tag{font-size:12px;text-transform:uppercase;font-weight:700;letter-spacing:.05em;margin-right:8px}
.prompt,.code{background:#f8fafc;border:1px dashed #c3cddd;padding:10px;border-radius:6px;margin-top:8px;font-size:14px;color:#1f2937;overflow-wrap:anywhere}
.score{font-size:60px;font-weight:800}small{color:#5b6474}.price{font-size:36px;font-weight:800}.ok{color:#15803d}.bad{color:#b91c1c}
.hero h1{font-size:46px;line-height:1.1}.eyebrow{display:inline-block;background:#fef3c7;color:#78350f;border:1px solid #fcd34d;border-radius:999px;padding:3px 10px;font-weight:700;letter-spacing:.08em}.cta{display:flex;flex-wrap:wrap;gap:12px;align-items:center}.cta input[name=url],.cta2 input[name=url]{flex:1;min-width:300px;margin:0}.own{display:block;width:100%;color:#374151;margin:4px 0 14px}.works{color:#4b5563}.faq details{background:#fff;border:1px solid #e3e8f0;border-radius:10px;padding:14px 16px;margin:8px 0}.faq summary{cursor:pointer;font-weight:600}.sample{opacity:.97}.blur{filter:blur(5px);user-select:none}.lock{background:#f5f8ff;border:1px solid #d6e0f5;border-radius:12px;padding:20px;margin:18px 0}h2{margin-top:36px}.cta2 h2{margin-top:0}nav{display:flex;flex-wrap:wrap;align-items:center;gap:4px 18px;margin-bottom:10px}nav a{color:#374151;text-decoration:none;padding:10px 0}nav .links{display:flex;gap:18px}nav a.navcta{margin-left:auto;padding:8px 14px;border:1px solid #2563eb;border-radius:8px;color:#1d4ed8;background:#fff;font-weight:600;min-height:44px;display:inline-flex;align-items:center}footer{margin-top:44px;padding-top:16px;border-top:1px solid #e3e8f0;color:#5b6474}.samplecta{margin:14px 0 0}.samplebtn{display:inline-flex;align-items:center;min-height:44px;padding:8px 14px;border:1px solid #2563eb;border-radius:8px;color:#1d4ed8;background:#fff;font-weight:600;text-decoration:none}.areahd{margin:14px 0 4px;color:#374151;font-weight:600}.areas{margin:0;padding-left:20px;color:#374151;line-height:1.7}.busy{display:none;margin:10px 0 0;color:#374151}form.sending .busy{display:block;width:100%}
*{box-sizing:border-box}img,pre,table{max-width:100%}.cmp{border-collapse:collapse;width:100%;font-size:.95em;margin:1em 0}.cmp th,.cmp td{border:1px solid #ddd;padding:8px;text-align:left;vertical-align:top}.cmp th{background:#f5f5f5}.wrap,.card,.grid div,.f,.lock{overflow-wrap:anywhere;min-width:0}
.plans{display:grid;grid-template-columns:repeat(4,1fr);grid-template-rows:auto auto 1fr auto;gap:14px;align-items:stretch}.plans>div{display:grid;grid-template-rows:subgrid;grid-row:span 4;row-gap:8px;background:#fff;border:1px solid #e3e8f0;border-radius:12px;padding:16px;color:#374151;min-width:0;overflow-wrap:anywhere}.plans .price{line-height:1.1}.pdesc{margin:0}.foot{display:flex;flex-direction:column;gap:8px;align-self:start}.pbtn{display:flex;align-items:center;justify-content:center;text-align:center;width:100%;min-height:58px;background:#2563eb;color:#fff;padding:8px 10px;border-radius:8px;text-decoration:none;font-size:15px;line-height:1.3}.phelp{display:block;color:#5b6474;line-height:1.35}
@media (max-width:640px){nav .links{order:3;flex-basis:100%;gap:22px}nav a{padding:12px 0}nav a.navcta{padding:8px 14px}.plans{grid-template-columns:1fr}.plans>div{grid-row:auto;display:flex;flex-direction:column}.foot{margin-top:6px;align-self:stretch}.pbtn{min-height:44px}.wrap{padding:24px 16px}.grid{grid-template-columns:1fr !important}h1,.hero h1{font-size:32px}.score{font-size:48px}.cta input[name=url],.cta2 input[name=url]{min-width:0;width:100%;flex-basis:100%}.card{padding:18px}form[style*=inline]{display:block !important;margin:10px 0 0 !important}button{max-width:100%;white-space:normal}}"""
SCAN_JS = '<script>(function(){var s=new URLSearchParams(location.search).get(\'src\');if(!s||!/^[a-z0-9-]{1,30}$/.test(s))return;document.querySelectorAll(\'form[action="/scan"]\').forEach(function(f){if(f.querySelector(\'input[name=src]\'))return;var i=document.createElement(\'input\');i.type=\'hidden\';i.name=\'src\';i.value=s;f.appendChild(i);});})();document.querySelectorAll(\'form[action="/scan"]\').forEach(function(f){var m=document.createElement(\'p\');m.className=\'busy\';m.setAttribute(\'role\',\'status\');m.textContent=\'Checking your app... this takes up to 30 seconds. Please keep this page open.\';f.appendChild(m);f.addEventListener(\'submit\',function(){f.classList.add(\'sending\');var b=f.querySelector(\'button\');if(b){b.disabled=true;b.textContent=\'Checking your app...\';}});});document.querySelectorAll(\'a[data-src]\').forEach(function(a){a.addEventListener(\'click\',function(){var f=document.getElementById(\'check\');if(!f)return;var i=f.querySelector(\'input[name=src]\');if(!i){i=document.createElement(\'input\');i.type=\'hidden\';i.name=\'src\';f.appendChild(i);}i.value=a.getAttribute(\'data-src\');var u=f.querySelector(\'input[name=url]\');if(u)setTimeout(function(){u.focus({preventScroll:true});},350);});});</script>'
FAVICON_SVG = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='14' fill='#2563eb'/><path d='M18 33l9 9 19-20' fill='none' stroke='#fff' stroke-width='7' stroke-linecap='round' stroke-linejoin='round'/><circle cx='51' cy='13' r='6' fill='#fcd34d'/></svg>"
OG_IMAGE_ALT = "VibeCheck Weekly: free check for exposed API keys, missing security headers and Google problems in AI-built apps"
def share_head(title, desc, extra_head=""):
    """Test 2026-10-24 (social-preview-image): large preview image on every page so shared links show a card, not a bare URL."""
    b = config.BASE_URL
    og = "" if "og:title" in extra_head else f"<meta property='og:title' content='{E(title)}'><meta property='og:description' content='{E(desc)}'>"
    return (og + f"<meta property='og:site_name' content='{E(config.APP_NAME)}'><meta property='og:image' content='{b}/og.png'><meta property='og:image:width' content='1200'>"
            f"<meta property='og:image:height' content='630'><meta property='og:image:alt' content='{E(OG_IMAGE_ALT)}'>"
            f"<meta name='twitter:card' content='summary_large_image'><meta name='twitter:site' content='@VibeCheck_Wkly'><meta name='twitter:image' content='{b}/og.png'>")
OG_PNG = open(__import__("os").path.join(__import__("os").path.dirname(__file__), "og.png"), "rb").read()
DEFAULT_DESC = "Weekly security and Google-visibility check for apps built with Lovable, Bolt, Cursor and Supabase."
def page(title, body, extra_head="", desc=None):
    return (f"<!doctype html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>{E(title)}</title>"
            f"<meta name=description content='{E(desc or DEFAULT_DESC)}'><link rel=icon type='image/svg+xml' href=/favicon.svg>{extra_head}{share_head(title, desc or DEFAULT_DESC, extra_head)}<style>{CSS}</style></head>"
            f"<body><div class=wrap><nav><a class=brand href=/><b>{E(config.APP_NAME)}</b></a><span class=links><a href=/pricing>Pricing</a><a href=/guides>Guides</a><a href=/tips>Tips</a></span><a class=navcta href='/?src=nav#check'>Free check</a></nav>{body}<footer><small>Questions or feedback? Email <a href='mailto:{config.SUPPORT_EMAIL}'>{config.SUPPORT_EMAIL}</a>.</small></footer></div>{SCAN_JS}</body></html>")
FAQ_LD = [
 ("Is the scan safe for my app?", "Yes. It is read-only and passive: VibeCheck loads your public pages and scripts like a normal visitor. No logins, no attacks, no writes and no database probing."),
 ("Do you need access to my code or Supabase?", "No. The check only uses what your site already serves publicly. Weekly monitoring asks you to add a small verification tag so only the owner can set it up."),
 ("Can it prove my database is secure?", "No outside scan can. VibeCheck flags the warning signs, such as exposed keys and Supabase usage, and gives you a prompt to have your AI tool audit your Row Level Security rules."),
 ("What is the fix prompt?", "A ready-made instruction you paste into Lovable, Bolt, Cursor or Replit so the AI fixes the issue for you."),
 ("Can I cancel monitoring?", "Yes, any time. The $9 report is a one-time payment, not a subscription."),
 ("How do I check if my Lovable app is secure?", "Check four things: no secret keys (such as the Supabase service_role key or an OpenAI key) in your live JavaScript, Row Level Security turned on for every Supabase table, private pages that refuse to load when you are logged out, and basic security headers. VibeCheck Weekly's free scan checks the keys, headers and Google visibility automatically."),
 ("Is it safe to have the Supabase anon key in my frontend?", "Yes, the anon key is designed to be public, as long as Row Level Security is on and your policies are correct. The service_role key bypasses all security rules and must never appear in browser code."),
]
def landing_head():
    b = config.BASE_URL
    app = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": config.APP_NAME, "url": b + "/",
           "applicationCategory": "SecurityApplication", "operatingSystem": "Web",
           "description": "A free, read-only security and Google-visibility scan for live apps built with Lovable, Bolt, Replit, v0, Cursor and Supabase, with optional weekly rescans.",
           "offers": [{"@type": "Offer", "name": "Free check", "price": "0", "priceCurrency": "USD"},
                      {"@type": "Offer", "name": "Full report (one time)", "price": "9", "priceCurrency": "USD"},
                      {"@type": "Offer", "name": "Solo weekly monitoring", "price": "19", "priceCurrency": "USD"},
                      {"@type": "Offer", "name": "Pro weekly monitoring (up to 5 apps)", "price": "49", "priceCurrency": "USD"}]}
    faq = {"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ_LD]}
    ld = lambda o: "<script type='application/ld+json'>" + json.dumps(o).replace("<", "\\u003c") + "</script>"
    t = f"{config.APP_NAME}: free security and Google check for AI-built apps"
    return (f"<link rel=canonical href='{b}/'><meta property='og:type' content='website'><meta property='og:url' content='{b}/'>"
            f"<meta property='og:title' content='{E(t)}'><meta property='og:description' content='{E(LANDING_DESC)}'>"
            + ld(app) + ld(faq))
LANDING_DESC = "Free 30-second check for apps built with Lovable, Bolt, Replit, v0 or Cursor: finds exposed API keys, Supabase service_role leaks, missing security headers and problems that keep Google from finding your site."
def landing():
    return page(f"{config.APP_NAME} – Is your AI-built app leaking keys?", """
<section class=hero><small class=eyebrow>FREE 30-SECOND CHECK</small>
<h1>Is your Lovable, Bolt or Cursor app leaking keys, or invisible to Google?</h1><!-- test 2026-10-26 hero-headline-names-builders -->
<p class=sub>Paste your app's URL. We read only what any visitor's browser can see and tell you, in plain English, what's exposed and what's hurting your search ranking, with fix prompts you can paste straight back into your AI tool.</p>
<form id=check class="card cta" method=post action=/scan>
<input type=text inputmode=url autocapitalize=off autocorrect=off spellcheck=false name=url required placeholder="myapp.lovable.app or yourdomain.com" aria-label="Your app URL">
<label class=own><input type=checkbox name=owner value=1 required> I own this app or am allowed to test it</label>
<button>Check my app free</button></form>
<p class=trust><small>Free, with no signup, no card and nothing to install. Read-only: we never log in or change anything.</small></p>
<p class=works>Works with apps built in <b>Lovable</b>, <b>Bolt</b>, <b>Cursor</b>, <b>Replit</b>, v0, or by hand.</p></section>
<h2>What a report looks like</h2>
<div class="card sample"><div><span class=score>58</span>/100 &nbsp; <span class=sub>2 critical · 3 warnings · 4 passed</span></div>
<div class="f critical"><span class=tag>critical</span><b>Supabase service_role key exposed</b><div>Found eyJhbGci…x9Qk in /assets/index-4f2a.js. This key bypasses all database security rules.</div>
<div class=prompt><b>Paste into your AI tool:</b> My frontend contains the Supabase service_role key. Remove it from all client code, use only the anon key in the browser…</div></div>
<div class="f warning"><span class=tag>warning</span><b>No sitemap.xml</b><div>Google has no map of your pages.</div></div>
<div class="f warning"><span class=tag>warning</span><b>Page has almost no readable text without JavaScript</b><div>Search engines may see an empty page.</div></div>
<div class="f pass"><span class=tag>pass</span><b>HTTPS is on</b></div><small>Example report for illustration.</small></div>
<p class=samplecta><a class=samplebtn href='#check' data-src=example>Get my own report free</a></p>
<h2>How it works</h2>
<div class=grid><div><b>1. Paste your URL</b><br>No signup, no code access, no install. Tick that it's your app.</div>
<div><b>2. See your score</b><br>Enter your email to see your score and every problem we found.</div>
<div><b>3. Fix it in minutes</b><br>Unlock the full report for $9 once, with a copy-paste fix prompt for every issue. Or have us re-check weekly.</div></div>
<h2>What we check</h2>
<div class=grid><div><b>Leaked secrets</b><br>OpenAI, Anthropic, Stripe, AWS, GitHub keys and Supabase service_role keys in your public code.</div>
<div><b>Security basics</b><br>HTTPS, redirects and the headers that block common attacks.</div>
<div><b>Google visibility</b><br>Leftover noindex tags, titles, descriptions, social previews, robots.txt, sitemap and empty single-page apps.</div></div>
<h2>Pricing</h2>
<div class=grid><div><b>Free check</b><div class=price>$0</div>Free scan with the list of issues found.</div>
<div><b>Full report</b><div class=price>$9</div>One-time. Every detail plus fix prompts.</div>
<div><b>Weekly monitoring</b><div class=price>$19<small>/mo</small></div>Re-checked every week, alerts on new issues. $49/mo for up to 5 apps.</div></div>
<p style='text-align:center'><small style='color:#5b6474'>+ sales tax where applicable</small></p>
<h2>FAQ</h2>
<div class=faq><details><summary>Is the scan safe for my app?</summary>Yes. It's read-only and passive: we load your public pages and scripts like a normal visitor. No logins, no attacks, no writes, no database probing.</details>
<details><summary>Do you need access to my code or Supabase?</summary>No. The check only uses what your site already serves publicly. Weekly monitoring asks you to add a small verification tag so only the owner can set it up.</details>
<details><summary>Can it prove my database is secure?</summary>No outside scan can. We flag the warning signs (exposed keys, Supabase usage) and give you a prompt to have your AI tool audit your Row Level Security rules.</details>
<details><summary>What's the fix prompt?</summary>A ready-made instruction you paste into Lovable, Bolt, Cursor or Replit so the AI fixes the issue for you.</details>
<details><summary>Can I cancel monitoring?</summary>Yes, any time. The $9 report is a one-time payment, not a subscription.</details>
<details><summary>How do I check if my Lovable app is secure?</summary>Check four things: no secret keys (such as the Supabase service_role key or an OpenAI key) in your live JavaScript, Row Level Security turned on for every Supabase table, private pages that refuse to load when you are logged out, and basic security headers. VibeCheck's free scan checks the keys, headers and visibility for you, and our <a href=/guides/is-my-lovable-app-secure>Lovable security checklist</a> covers the rest.</details>
<details><summary>Is it safe to have the Supabase anon key in my frontend?</summary>Yes, the anon key is designed to be public, as long as Row Level Security is on and your policies are correct. The service_role key is different: it bypasses all security rules and must never appear in browser code. See the <a href=/guides/supabase-rls-checklist>Supabase RLS checklist</a>.</details></div>
<div class="card cta2"><h2>Find out in 30 seconds.</h2><form method=post action=/scan>
<input type=text inputmode=url autocapitalize=off autocorrect=off spellcheck=false name=url required placeholder="myapp.lovable.app or yourdomain.com" aria-label="Your app URL">
<label class=own><input type=checkbox name=owner value=1 required> I own this app or am allowed to test it</label><button>Check my app free</button></form></div>""", landing_head(), desc=LANDING_DESC)
def pricing():
    p = config.PLANS
    return page("Pricing", f"""<h1>Pricing</h1><p class=sub>Your first check is free. Weekly monitoring re-checks your app every week and emails you only what changed.</p>
<div class=plans>
<div><b>Free</b><div class=price>$0</div><p class=pdesc>Free scan with the list of issues found.</p><div class=foot><a class=pbtn href='/#check'>Start a free check</a></div></div>
<div><b>Full report, $9 one-time</b><div class=price>$9</div><p class=pdesc>The details behind each issue and step-by-step fixes for one scan, no subscription.</p><div class=foot><a class=pbtn href='/#check'>Scan, then unlock for $9</a><small class=phelp>Run a free scan first. The $9 unlock appears with your results.</small></div></div>
<div><b>{p['solo']['name']}</b><div class=price>${p['solo']['price']}<small>/mo</small></div><p class=pdesc>Weekly monitoring for 1 app, alerts on new issues, fix prompts.</p><div class=foot><a class=pbtn href='/#check'>Start free, then get Solo</a></div></div>
<div><b>{p['pro']['name']}</b><div class=price>${p['pro']['price']}<small>/mo</small></div><p class=pdesc>Weekly monitoring for up to 5 apps.</p><div class=foot><a class=pbtn href='/#check'>Start free, then get Pro</a></div></div></div>
<p style='text-align:center'><small style='color:#5b6474'>+ sales tax where applicable</small></p>
<p><small>Plans start from a free check of your app: scan it, confirm you own it, then choose Solo or Pro on your site page.</small></p>
<div class="card cta2"><h2>Start with the free check</h2><p class=sub>Paste your live URL and see your score and the list of issues in about 30 seconds. You only pay if you want the fixes or weekly monitoring.</p>
<form method=post action=/scan><input type=hidden name=src value="pricing"><input type=text inputmode=url autocapitalize=off autocorrect=off spellcheck=false name=url required placeholder="myapp.lovable.app or yourdomain.com" aria-label="Your app URL">
<label class=own><input type=checkbox name=owner value=1 required> I own this app or am allowed to test it</label><button>Check my app free</button></form></div>""", desc="VibeCheck Weekly pricing: a free security and Google-visibility check, a $9 one-time full report with fixes, or weekly monitoring at $19/month for 1 app or $49/month for up to 5 apps.")
def message(title, text, code=None):
    return page(title, f"<h1>{E(title)}</h1><p class=sub>{text}</p><a href=/>Back to start</a>")
def site_page(site, account, scans, ins, verify_error=None, weekly_count=0):
    k = site["manage_key"]; verified = bool(site["verified_at"])
    out = [f"<small>YOUR SITE</small><h1>{E(site['host'])}</h1>"]
    if not verified:
        err = f"<p class=bad>{E(verify_error)}</p>" if verify_error else ""
        out.append(f"""<div class=card><b>Step 1: prove you own this app.</b> Add <u>one</u> of these, deploy, then press Verify.
<p>Option A: put this tag inside the &lt;head&gt; of your home page:</p><div class=code>{E(ins['meta'])}</div>
<p>Option B: serve a file at <b>{E(ins['file_path'])}</b> containing only:</p><div class=code>{E(ins['file_body'])}</div>
<p><small>Tip for Lovable/Bolt/Cursor: paste “Add this exact meta tag to the head of index.html: {E(ins['meta'])}” into your AI tool.</small></p>{err}
<form method=post action=/site/{k}/verify><button>Verify and run my free check</button></form>
<p><small>Once verified, you can start weekly monitoring here: Solo $19/mo (1 app) or Pro $49/mo (up to 5 apps). + sales tax where applicable.</small></p></div>""")
    else:
        out.append(f"<div class=card><span class=ok>✔ Ownership verified</span> &nbsp; Plan: <b>{E(account['plan'].title())}</b> &nbsp; Weekly monitoring: <b>{'on' if site['weekly'] else 'off'}</b>"
                   f"<form method=post action=/site/{k}/scan style='margin-top:14px'><button>Run a new check</button></form></div>")
        if not site["weekly"]:
            if account["plan"] == "pro" and weekly_count < config.PLANS["pro"]["apps"]:
                out.append(f"<div class=card><form method=post action=/site/{k}/monitor><button class=alt>Add this app to weekly monitoring ({weekly_count}/5 used)</button></form></div>")
            else:
                out.append(f"""<div class=card><b>Keep it safe every week.</b><p>We re-check every week and email you when something new breaks.</p>
<form method=post action=/site/{k}/checkout style='display:inline'><input type=hidden name=plan value=solo><button class=alt>Monitor 1 app – $19/mo</button></form>
<form method=post action=/site/{k}/checkout style='display:inline;margin-left:10px'><input type=hidden name=plan value=pro><button class=alt>Monitor up to 5 apps – $49/mo</button></form><p><small style='color:#5b6474'>+ sales tax where applicable</small></p></div>""")
    if scans:
        out.append("<h2>Reports</h2>" + "".join(f"<div class=f><a href=/r/{s['token']}>{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(s['created_at']))}</a> &nbsp; score <b>{s['score']}</b>/100</div>" for s in scans))
    out.append("<p><small>Bookmark this page: it is your private link for this site.</small></p>")
    return page(site["host"], "".join(out))
def report(scan, mode="full"):
    """mode: teaser (no email yet), titles (email given), full (unlocked)."""
    r = json.loads(scan["result"]); m = r["meta"]; tok = scan["token"]
    order = {"critical":0,"warning":1,"fix":2,"info":3,"pass":4}
    items = sorted(r["findings"], key=lambda x: order.get(x["severity"], 5))
    c = {k: sum(1 for x in items if x["severity"] == k) for k in ("critical","warning","info","pass")}
    head = f"<small>REPORT</small><h1>{E(m.get('final_url', m['url']))}</h1>"
    if mode == "teaser":
        n = c["critical"] + c["warning"]; what = f"the {n} issues we found" if n else "your full results"
        # test 2026-10-23 (teaser-issue-areas): before the email box, show where the issues are (area + count); titles stay hidden
        if n:
            found = f"We found <b>{n} issue{'s' if n != 1 else ''}</b>" + (f", <b>{c['critical']} critical</b>." if c["critical"] else ", none critical.")
        else:
            found = "We found no critical or warning issues."
        areas = [(a, sum(1 for x in items if x["area"] == a and x["severity"] in ("critical", "warning"))) for a in ("Security", "Supabase", "Google visibility", "Speed", "Basics")]
        alist = "".join(f"<li><b>{a}:</b> {k} issue{'s' if k != 1 else ''}</li>" for a, k in areas if k)
        abox = f"<p class=areahd>Where we found them:</p><ul class=areas>{alist}</ul>" if alist else ""
        return page("Your report", head + f"""<div class=card><span class="score blur">{r['score']}</span>/100 &nbsp; <span class=sub>Your check is done. {found}</span>{abox}</div>
<form class=lock method=post action=/r/{tok}/email><b>Your free results are ready.</b><p>Enter your email to see your score and {what}. It's free, and no card is needed.</p>
<input type=email name=email required placeholder="you@example.com" aria-label="Your email" autocomplete=email><button>Show my free results</button><p><small>We'll also email you a link to this report. Unsubscribe any time.</small></p></form>""")
    out = [head, f"<div class=card><span class=score>{r['score']}</span>/100 &nbsp; <span class=sub>{c['critical']} critical · {c['warning']} warnings · {c['info']} notes · {c['pass']} passed</span><br>"
           f"<small>Scanned {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(scan['created_at']))} · {m.get('scripts_checked',0)} script files checked · HTML loaded in {m.get('load_seconds','?')}s</small></div>"]
    if mode == "titles":
        # test 2026-10-22 (unlock-box-names-issues): headline names the issue count and the top issue
        n = c["critical"] + c["warning"]; top = next((x["title"] for x in items if x["severity"] in ("critical", "warning")), None)
        hl = f"Get the fix for {'this issue' if n == 1 else ('both issues' if n == 2 else f'all {n} issues')}: $9, one time." if n else "Unlock the full report: $9, one time."
        first = f" Starting with: <b>{E(top)}</b>." if top else ""
        out.append(f"""<div class=lock><b>{hl}</b><p>See exactly where each problem is and get a copy-paste fix prompt for your AI tool for every issue.{first}</p>
<form method=post action=/r/{tok}/unlock style='display:inline'><button>{'Show me the fixes – $9' if n else 'Unlock full report – $9'}</button></form>
<form method=post action=/r/{tok}/monitor style='display:inline;margin-left:10px'><button class=alt>Or monitor weekly from $19/mo</button></form><p><small>Weekly plans include full reports. + sales tax where applicable.</small></p></div>""")
    for area in ("Security", "Supabase", "Google visibility", "Speed", "Basics"):
        sec = [x for x in items if x["area"] == area and (mode == "full" or x["severity"] != "fix")]
        if not sec: continue
        out.append(f"<h2>{area}</h2>")
        for x in sec:
            lab = "fix prompt" if x["severity"] == "fix" else x["severity"]
            if mode == "full":
                fix = f"<div class=prompt><b>Paste into your AI tool:</b> {E(x['fix'])}</div>" if x.get("fix") else ""
                out.append(f"<div class='f {x['severity']}'><span class=tag>{lab}</span><b>{E(x['title'])}</b><div>{E(x['detail'])}</div>{fix}</div>")
            else:
                lockd = " <small>🔒 details and fix prompt in full report</small>" if x["severity"] in ("critical","warning","info") else ""
                out.append(f"<div class='f {x['severity']}'><span class=tag>{lab}</span><b>{E(x['title'])}</b>{lockd}</div>")
    if mode == "full":
        # test 2026-10-24 (full-report-keep-fixed-copy): monitoring upsell names the app and says why fixes come undone
        host = E(urllib.parse.urlparse(m.get("final_url") or m["url"]).hostname or "your app")
        out.append(f"""<div class=lock><b>Keep these fixes in place.</b><p>Your next prompt or update can quietly bring an issue back. We re-check <b>{host}</b> every week and email you only when something new appears. Cancel any time.</p>
<form method=post action=/r/{tok}/monitor style='display:inline'><button class=alt>Monitor {host} weekly – $19/mo</button></form><p><small>Up to 5 apps for $49/mo. + sales tax where applicable.</small></p></div>""")
    out.append("<p><small>This passive check only reads publicly served pages and files. It cannot confirm database rules (RLS) or server-side logic.</small></p>")
    return page("Report", "".join(out))
def report_email(site, scan, prev_score=None):
    host = site["host"] if site else (scan.get("url") or "")
    site = {"host": host}
    url = f"{config.BASE_URL}/r/{scan['token']}"
    delta = "" if prev_score is None else f" (last week: {prev_score})"
    html_ = f"<p>Your {E(config.APP_NAME)} check for <b>{E(site['host'])}</b> is ready.</p><p>Score: <b>{scan['score']}/100</b>{delta}</p><p><a href='{url}'>Open your report</a></p>"
    return f"{config.APP_NAME} report for {site['host']}: {scan['score']}/100", html_, f"Score {scan['score']}/100{delta}. Report: {url}"
