import html, json, time
from . import config
E = html.escape
CSS = """body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:0;background:#0b1020;color:#e8ecf5}
a{color:#7cc4ff}.wrap{max-width:860px;margin:0 auto;padding:40px 24px}h1{font-size:40px;margin:.2em 0}
.sub{color:#aab3c8;font-size:19px;line-height:1.5}.card{background:#141b31;border:1px solid #243052;border-radius:14px;padding:24px;margin:22px 0}
input[type=url],input[type=email]{width:100%;box-sizing:border-box;padding:13px;margin:6px 0 14px;border-radius:8px;border:1px solid #33416b;background:#0b1020;color:#fff;font-size:16px}
button{background:#3b82f6;color:#fff;border:0;border-radius:8px;padding:13px 20px;font-size:16px;cursor:pointer}button.alt{background:#7c3aed}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.grid div{background:#141b31;border:1px solid #243052;border-radius:12px;padding:16px;color:#c7cfe0}.grid div div{background:none;border:0;padding:0;border-radius:0}
.f{border-left:5px solid #555;padding:12px 16px;margin:10px 0;background:#141b31;border-radius:8px}
.critical{border-color:#ef4444}.warning{border-color:#f59e0b}.info{border-color:#60a5fa}.pass{border-color:#22c55e}.fix{border-color:#a78bfa}
.tag{font-size:12px;text-transform:uppercase;font-weight:700;letter-spacing:.05em;margin-right:8px}
.prompt,.code{background:#0b1020;border:1px dashed #3b4a78;padding:10px;border-radius:6px;margin-top:8px;font-size:14px;color:#d6dcf0;word-break:break-all}
.score{font-size:60px;font-weight:800}small{color:#8a93aa}.price{font-size:36px;font-weight:800}.ok{color:#22c55e}.bad{color:#f87171}
.hero h1{font-size:46px;line-height:1.1}.eyebrow{color:#7cc4ff;font-weight:700;letter-spacing:.08em}.cta{display:flex;flex-wrap:wrap;gap:12px;align-items:center}.cta input[type=url],.cta2 input[type=url]{flex:1;min-width:300px;margin:0}.own{display:block;width:100%;color:#c7cfe0;margin:4px 0 14px}.works{color:#aab3c8}.faq details{background:#141b31;border:1px solid #243052;border-radius:10px;padding:14px 16px;margin:8px 0}.faq summary{cursor:pointer;font-weight:600}.sample{opacity:.97}.blur{filter:blur(5px);user-select:none}.lock{background:#1e2745;border:1px solid #3b4a78;border-radius:12px;padding:20px;margin:18px 0}h2{margin-top:36px}nav{display:flex;gap:18px;margin-bottom:10px}nav a{color:#aab3c8;text-decoration:none}.busy{display:none;margin:10px 0 0;color:#c7cfe0}form.sending .busy{display:block;width:100%}
*{box-sizing:border-box}img,pre,table{max-width:100%}.wrap,.card,.grid div,.f,.lock{overflow-wrap:anywhere;min-width:0}
@media (max-width:640px){.wrap{padding:24px 16px}.grid{grid-template-columns:1fr !important}h1,.hero h1{font-size:32px}.score{font-size:48px}.cta input[type=url],.cta2 input[type=url]{min-width:0;width:100%;flex-basis:100%}.card{padding:18px}form[style*=inline]{display:block !important;margin:10px 0 0 !important}button{max-width:100%;white-space:normal}}"""
SCAN_JS = '<script>document.querySelectorAll(\'form[action="/scan"]\').forEach(function(f){var m=document.createElement(\'p\');m.className=\'busy\';m.setAttribute(\'role\',\'status\');m.textContent=\'Checking your app... this takes about 30 seconds. Please keep this page open.\';f.appendChild(m);f.addEventListener(\'submit\',function(){f.classList.add(\'sending\');var b=f.querySelector(\'button\');if(b){b.disabled=true;b.textContent=\'Checking your app...\';}});});</script>'
DEFAULT_DESC = "Weekly security and Google-visibility check for apps built with Lovable, Bolt, Cursor and Supabase."
def page(title, body, extra_head="", desc=None):
    return (f"<!doctype html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>{E(title)}</title>"
            f"<meta name=description content='{E(desc or DEFAULT_DESC)}'>{extra_head}<style>{CSS}</style></head>"
            f"<body><div class=wrap><nav><a href=/><b>{E(config.APP_NAME)}</b></a><a href=/pricing>Pricing</a><a href=/guides>Guides</a></nav>{body}</div>{SCAN_JS}</body></html>")
def landing():
    return page(f"{config.APP_NAME} – Is your AI-built app leaking keys?", """
<section class=hero><small class=eyebrow>FREE 30-SECOND CHECK</small>
<h1>Your AI-built app works. But is it leaking keys, or invisible to Google?</h1>
<p class=sub>Paste your app's URL. We read only what any visitor's browser can see and tell you, in plain English, what's exposed and what's hurting your search ranking, with fix prompts you can paste straight back into your AI tool.</p>
<form id=check class="card cta" method=post action=/scan>
<input type=url name=url required placeholder="https://myapp.lovable.app" aria-label="Your app URL">
<label class=own><input type=checkbox name=owner value=1 required> I own this app or am allowed to test it</label>
<button>Check my app free</button></form>
<p class=works>Works with apps built in <b>Lovable</b>, <b>Bolt</b>, <b>Cursor</b>, <b>Replit</b>, v0, or by hand.</p></section>
<h2>What a report looks like</h2>
<div class="card sample"><div><span class=score>58</span>/100 &nbsp; <span class=sub>2 critical · 3 warnings · 4 passed</span></div>
<div class="f critical"><span class=tag>critical</span><b>Supabase service_role key exposed</b><div>Found eyJhbGci…x9Qk in /assets/index-4f2a.js. This key bypasses all database security rules.</div>
<div class=prompt><b>Paste into your AI tool:</b> My frontend contains the Supabase service_role key. Remove it from all client code, use only the anon key in the browser…</div></div>
<div class="f warning"><span class=tag>warning</span><b>No sitemap.xml</b><div>Google has no map of your pages.</div></div>
<div class="f warning"><span class=tag>warning</span><b>Page has almost no readable text without JavaScript</b><div>Search engines may see an empty page.</div></div>
<div class="f pass"><span class=tag>pass</span><b>HTTPS is on</b></div><small>Example report for illustration.</small></div>
<h2>How it works</h2>
<div class=grid><div><b>1. Paste your URL</b><br>No signup, no code access, no install. Tick that it's your app.</div>
<div><b>2. See your score</b><br>Enter your email to see your score and every problem we found.</div>
<div><b>3. Fix it in minutes</b><br>Unlock the full report for $9 once, with a copy-paste fix prompt for every issue. Or have us re-check weekly.</div></div>
<h2>What we check</h2>
<div class=grid><div><b>Leaked secrets</b><br>OpenAI, Anthropic, Stripe, AWS, GitHub keys and Supabase service_role keys in your public code.</div>
<div><b>Security basics</b><br>HTTPS, redirects and the headers that block common attacks.</div>
<div><b>Google visibility</b><br>Titles, descriptions, social previews, robots.txt, sitemap and empty single-page apps.</div></div>
<h2>Pricing</h2>
<div class=grid><div><b>Free check</b><div class=price>$0</div>Score and list of problems.</div>
<div><b>Full report</b><div class=price>$9</div>One-time. Every detail plus fix prompts.</div>
<div><b>Weekly monitoring</b><div class=price>$19<small>/mo</small></div>Re-checked every week, alerts on new issues. $49/mo for up to 5 apps.</div></div>
<h2>FAQ</h2>
<div class=faq><details><summary>Is the scan safe for my app?</summary>Yes. It's read-only and passive: we load your public pages and scripts like a normal visitor. No logins, no attacks, no writes, no database probing.</details>
<details><summary>Do you need access to my code or Supabase?</summary>No. The check only uses what your site already serves publicly. Weekly monitoring asks you to add a small verification tag so only the owner can set it up.</details>
<details><summary>Can it prove my database is secure?</summary>No outside scan can. We flag the warning signs (exposed keys, Supabase usage) and give you a prompt to have your AI tool audit your Row Level Security rules.</details>
<details><summary>What's the fix prompt?</summary>A ready-made instruction you paste into Lovable, Bolt, Cursor or Replit so the AI fixes the issue for you.</details>
<details><summary>Can I cancel monitoring?</summary>Yes, any time. The $9 report is a one-time payment, not a subscription.</details></div>
<div class="card cta2"><h2>Find out in 30 seconds.</h2><form method=post action=/scan>
<input type=url name=url required placeholder="https://myapp.lovable.app" aria-label="Your app URL">
<label class=own><input type=checkbox name=owner value=1 required> I own this app or am allowed to test it</label><button>Check my app free</button></form></div>""")
def pricing():
    p = config.PLANS
    return page("Pricing", f"""<h1>Pricing</h1><p class=sub>Your first check is free. Weekly monitoring re-checks your app every week and emails you only what changed.</p>
<div class=grid style='grid-template-columns:1fr 1fr 1fr'>
<div><b>Free</b><div class=price>$0</div>One full scan of your app, with the issue list.<br><a href='/#check' style='display:inline-block;margin-top:14px;background:#3b82f6;color:#fff;padding:11px 18px;border-radius:8px;text-decoration:none'>Start a free check</a></div>
<div><b>{p['solo']['name']}</b><div class=price>${p['solo']['price']}<small>/mo</small></div>Weekly monitoring for 1 app, alerts on new issues, fix prompts.<br><a href='/#check' style='display:inline-block;margin-top:14px;background:#3b82f6;color:#fff;padding:11px 18px;border-radius:8px;text-decoration:none'>Start free, then get Solo</a></div>
<div><b>{p['pro']['name']}</b><div class=price>${p['pro']['price']}<small>/mo</small></div>Weekly monitoring for up to 5 apps.<br><a href='/#check' style='display:inline-block;margin-top:14px;background:#3b82f6;color:#fff;padding:11px 18px;border-radius:8px;text-decoration:none'>Start free, then get Pro</a></div></div>
<p><small>Plans start from a free check of your app: scan it, confirm you own it, then choose Solo or Pro on your site page.</small></p>""")
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
<p><small>Once verified, you can start weekly monitoring here: Solo $19/mo (1 app) or Pro $49/mo (up to 5 apps).</small></p></div>""")
    else:
        out.append(f"<div class=card><span class=ok>✔ Ownership verified</span> &nbsp; Plan: <b>{E(account['plan'].title())}</b> &nbsp; Weekly monitoring: <b>{'on' if site['weekly'] else 'off'}</b>"
                   f"<form method=post action=/site/{k}/scan style='margin-top:14px'><button>Run a new check</button></form></div>")
        if not site["weekly"]:
            if account["plan"] == "pro" and weekly_count < config.PLANS["pro"]["apps"]:
                out.append(f"<div class=card><form method=post action=/site/{k}/monitor><button class=alt>Add this app to weekly monitoring ({weekly_count}/5 used)</button></form></div>")
            else:
                out.append(f"""<div class=card><b>Keep it safe every week.</b><p>We re-check every week and email you when something new breaks.</p>
<form method=post action=/site/{k}/checkout style='display:inline'><input type=hidden name=plan value=solo><button class=alt>Monitor 1 app – $19/mo</button></form>
<form method=post action=/site/{k}/checkout style='display:inline;margin-left:10px'><input type=hidden name=plan value=pro><button class=alt>Monitor up to 5 apps – $49/mo</button></form></div>""")
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
        return page("Your report", head + f"""<div class=card><span class="score blur">{r['score']}</span>/100 &nbsp; <span class=sub>Your check is done. We found <b>{c['critical']} critical</b> and <b>{c['warning']} warning</b> issues.</span></div>
<form class=lock method=post action=/r/{tok}/email><b>Where should we send your results?</b><p>Enter your email to see your score and the full list of problems.</p>
<input type=email name=email required placeholder="you@example.com"><button>Show my results</button><p><small>We'll email you a link to this report. Unsubscribe any time.</small></p></form>""")
    out = [head, f"<div class=card><span class=score>{r['score']}</span>/100 &nbsp; <span class=sub>{c['critical']} critical · {c['warning']} warnings · {c['info']} notes · {c['pass']} passed</span><br>"
           f"<small>Scanned {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(scan['created_at']))} · {m.get('scripts_checked',0)} script files checked · HTML loaded in {m.get('load_seconds','?')}s</small></div>"]
    if mode == "titles":
        out.append(f"""<div class=lock><b>Unlock the full report: $9, one time.</b><p>See exactly where each problem is and get a copy-paste fix prompt for your AI tool for every issue.</p>
<form method=post action=/r/{tok}/unlock style='display:inline'><button>Unlock full report – $9</button></form>
<form method=post action=/r/{tok}/monitor style='display:inline;margin-left:10px'><button class=alt>Or monitor weekly from $19/mo</button></form><p><small>Weekly plans include full reports.</small></p></div>""")
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
        out.append(f"<div class=lock><b>Keep it fixed.</b> Apps change every week. <form method=post action=/r/{tok}/monitor style='display:inline;margin-left:10px'><button class=alt>Monitor weekly from $19/mo</button></form></div>")
    out.append("<p><small>This passive check only reads publicly served pages and files. It cannot confirm database rules (RLS) or server-side logic.</small></p>")
    return page("Report", "".join(out))
def report_email(site, scan, prev_score=None):
    host = site["host"] if site else (scan.get("url") or "")
    site = {"host": host}
    url = f"{config.BASE_URL}/r/{scan['token']}"
    delta = "" if prev_score is None else f" (last week: {prev_score})"
    html_ = f"<p>Your {E(config.APP_NAME)} check for <b>{E(site['host'])}</b> is ready.</p><p>Score: <b>{scan['score']}/100</b>{delta}</p><p><a href='{url}'>Open your report</a></p>"
    return f"{config.APP_NAME} report for {site['host']}: {scan['score']}/100", html_, f"Score {scan['score']}/100{delta}. Report: {url}"
