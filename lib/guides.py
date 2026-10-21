"""Helpful SEO guide pages, each ending with a call to the free scan."""
from . import config
from .views import page, E

CTA = """<div class="card cta2"><h2>Check your app in about 30 seconds</h2>
<p class=sub>Paste your live URL. The free check reads only what any visitor's browser can see and lists what is exposed and what is holding back your search visibility.</p>
<form method=post action=/scan><input type=hidden name=src value="{src}"><input type=url name=url required placeholder="https://myapp.lovable.app" aria-label="Your app URL">
<label class=own><input type=checkbox name=owner value=1 required> I own this app or am allowed to test it</label><button>Check my app free</button></form></div>"""
def cta(src): return CTA.replace("{src}", src)

GUIDES = {
"is-my-lovable-app-secure": dict(
 title="Is my Lovable app secure? A practical checklist",
 desc="How to check a Lovable app for exposed keys, Supabase Row Level Security gaps and missing security headers before real users arrive.",
 body="""<p class=sub>Lovable gets an app from idea to live link quickly. Security is still your responsibility once real people sign up. These are the checks worth doing before you share the link widely.</p>
<h2>1. Know which keys are meant to be public</h2>
<p>Every Lovable app that uses Supabase ships a project URL and an <b>anon</b> (public) key to the browser. That is expected: the anon key is designed to be public, and your database rules decide what it can do.</p>
<p>The <b>service_role</b> key is different. It bypasses all database rules and must never appear in frontend code. The same applies to private keys for OpenAI, Anthropic, Stripe (keys starting with sk_live_) and similar services. If one of these is in your published JavaScript, anyone can copy it.</p>
<p><b>How to check:</b> open your live app, open the browser developer tools, and search the loaded scripts for <code>service_role</code>, <code>sk_live_</code> and <code>sk-</code>. If you find one, rotate the key at the provider first, then move the call that uses it to a server-side function.</p>
<h2>2. Turn on Row Level Security for every table</h2>
<p>Because the anon key is public, Row Level Security (RLS) is what stops one user from reading or changing another user's data. A table with RLS off can be read by anyone who has your public key. See our <a href=/guides/supabase-rls-checklist>Supabase RLS checklist</a> for the step-by-step version.</p>
<h2>3. Test your pages while logged out</h2>
<p>Open a private browser window and visit admin pages, dashboards and any URL that contains a record ID. If data loads without signing in, or changing an ID shows someone else's record, access control is missing on the server side. Hiding a button in the interface does not protect the data behind it.</p>
<h2>4. Add basic security headers</h2>
<p>Headers such as Content-Security-Policy, X-Content-Type-Options, Referrer-Policy and a frame policy reduce the impact of common attacks like clickjacking and script injection. Many quickly built apps ship without most of them.</p>
<h2>5. Re-check after every big change</h2>
<p>Each new prompt can change your code. A setting that was fine last week can change after a refactor, so a regular re-check matters more than a single audit.</p>
<h2>What an outside scan can and cannot tell you</h2>
<p>A scan of your live site can find keys in public code, missing headers and visibility problems. It cannot see your database rules directly, so RLS should also be reviewed inside Supabase.</p>"""),
"supabase-rls-checklist": dict(
 title="Supabase RLS checklist for AI-built apps",
 desc="A step-by-step Supabase Row Level Security checklist for apps built with Lovable, Bolt, Cursor or v0: enabling RLS, writing policies and testing them.",
 body="""<p class=sub>Most AI app builders connect to Supabase and call the database straight from the browser using the public anon key. That setup is safe only if Row Level Security (RLS) is on and the policies are correct.</p>
<h2>Why RLS matters</h2>
<p>The anon key is included in your frontend code and anyone can read it. Without RLS, that key can read, and sometimes change, every row in a table. With RLS on and no policies, the table is locked. Policies then open up exactly the access each user should have.</p>
<h2>The checklist</h2>
<ol>
<li><b>RLS is enabled on every table in the public schema.</b> In the Supabase dashboard, open Table Editor or Authentication &gt; Policies and confirm none are marked as unrestricted. Supabase's Security Advisor also flags tables without RLS.</li>
<li><b>Each table has policies for the actions it needs.</b> Write separate policies for select, insert, update and delete instead of one broad policy.</li>
<li><b>Policies check the signed-in user.</b> For user-owned rows, compare the owner column with <code>auth.uid()</code>, for example <code>user_id = auth.uid()</code>.</li>
<li><b>Insert and update policies use WITH CHECK.</b> Otherwise a user may be able to create or move a row so that it belongs to someone else.</li>
<li><b>Nothing uses "true" as a policy unless the data really is public.</b> A policy of <code>using (true)</code> means everyone can read the table.</li>
<li><b>Storage buckets have policies too.</b> Files in Supabase Storage are protected by their own policies, separate from your tables.</li>
<li><b>The service_role key is server-side only.</b> It bypasses RLS completely, so it must never appear in browser code.</li>
<li><b>You have tested as a second user.</b> Sign up with a second account and try to read or edit the first account's data. The request should fail.</li>
</ol>
<h2>A prompt you can give your AI builder</h2>
<p class=prompt>Review every table in my Supabase public schema. Enable Row Level Security on any table where it is off. For each table, add separate select, insert, update and delete policies so users can only access rows where user_id = auth.uid(), and use WITH CHECK on insert and update. List any table you think should stay public and explain why before changing it.</p>
<h2>Where a live scan helps</h2>
<p>A scan of your live site cannot read your RLS policies, but it can confirm your app uses Supabase, check that no service_role key is exposed, and flag the other issues that tend to appear alongside RLS gaps.</p>"""),
"why-google-cant-find-your-ai-built-app": dict(
 title="Why Google can't find your AI-built app",
 desc="Common reasons apps built with Lovable, Bolt, Replit or v0 don't show up in Google: noindex tags, missing titles, no sitemap and pages that are empty without JavaScript.",
 body="""<p class=sub>Your app is live and the link works, but searching for it on Google shows nothing. These are the most common causes for apps built with AI tools, and each one can usually be fixed in a single prompt.</p>
<h2>1. A noindex tag was left on</h2>
<p>A <code>&lt;meta name="robots" content="noindex"&gt;</code> tag or an <code>X-Robots-Tag: noindex</code> header tells Google not to list the page. These are often added during development and forgotten at launch. View your page source and search for "noindex".</p>
<h2>2. robots.txt blocks crawlers</h2>
<p>Visit yourapp.com/robots.txt. A line reading <code>Disallow: /</code> under <code>User-agent: *</code> blocks the whole site.</p>
<h2>3. No sitemap</h2>
<p>A sitemap.xml lists the pages you want indexed. Without one, Google has to discover pages through links alone, which is slow for a new site with few links pointing to it. Add a sitemap and submit it in Google Search Console.</p>
<h2>4. Missing or generic titles and descriptions</h2>
<p>Many generated apps use the same title on every page, or a placeholder such as the project name. Each page needs a unique, descriptive title and meta description so Google knows what it is about and what to show in results.</p>
<h2>5. The page is empty without JavaScript</h2>
<p>Single-page apps often send an almost empty HTML file and build everything in the browser. Google can render JavaScript, but it may do so later and less reliably. Pre-rendering or server-side rendering for public pages, such as your home page, gives search engines real text to read.</p>
<h2>6. No social preview tags</h2>
<p>Open Graph tags (og:title, og:description, og:image) control how your link looks when shared. They don't directly affect ranking, but a clear preview helps people click, and shared links help a new site get found.</p>
<h2>7. The site is too new or has no links</h2>
<p>Even a well-built site takes time to be crawled. Register it in Google Search Console, submit the sitemap and request indexing for the home page.</p>"""),
"api-key-exposed-in-frontend": dict(
 title="Is my API key exposed in my AI-built app? How to check and fix it",
 desc="How to tell if an OpenAI, Stripe or Supabase service_role key is visible in the frontend of an app built with Lovable, Bolt, Replit, v0 or Cursor, and what to do if it is.",
 body="""<p class=sub>AI app builders often wire up an API by pasting the key right into the code. If that code runs in the browser, anyone who visits your site can find the key and use it on your bill. Here is how to check in a few minutes and how to fix it.</p>
<h2>1. Know which keys can be public</h2>
<p>Some keys are made to be seen. The Supabase project URL and <b>anon</b> key, a Stripe <b>publishable</b> key (pk_live_) and a Firebase web config are all fine in the browser. Your database rules and server settings decide what they can do.</p>
<p>Other keys must stay secret. These include the Supabase <b>service_role</b> key, Stripe secret keys (sk_live_), and keys for OpenAI (sk-), Anthropic (sk-ant-), Resend, SendGrid and similar services. If one of these reaches the browser, treat it as leaked.</p>
<h2>2. Search your live site</h2>
<p>Open your live app, not the editor preview. Open the browser developer tools, go to the Sources or Network tab, and search all loaded files for <code>service_role</code>, <code>sk_live_</code>, <code>sk-</code> and <code>Bearer</code>. Also check the Network tab while you use the app. If a request goes straight from the browser to api.openai.com or api.stripe.com with a secret key in the header, the key is exposed.</p>
<h2>3. Check environment variable names</h2>
<p>Tools like Vite and Next.js copy some environment variables into the browser code on purpose. Any variable that starts with <code>VITE_</code>, <code>NEXT_PUBLIC_</code> or <code>REACT_APP_</code> ends up public. A secret key stored under one of these names is not hidden, even though it lives in a .env file.</p>
<h2>4. Check your code history</h2>
<p>If your project is on GitHub and the repo is public, a key committed once is still in the history after you delete it. Search the repo, and assume any key that was ever committed is leaked.</p>
<h2>5. If you find a secret key, fix it in this order</h2>
<ol>
<li><b>Rotate the key first.</b> Create a new key at the provider and delete the old one. Removing it from your code does not help if someone already copied it.</li>
<li><b>Move the call to the server.</b> Put the request in a server-side function, such as a Supabase Edge Function, a Next.js API route or a Replit backend, and store the key as a server secret. Our guide on <a href=/guides/hide-api-keys-in-ai-built-apps>how to hide API keys in a Lovable, Bolt, v0 or Cursor app</a> shows how, step by step.</li>
<li><b>Check your usage and billing.</b> Look for charges or requests you don't recognize, and set a spending limit where the provider allows it.</li>
</ol>
<h2>A prompt you can give your AI builder</h2>
<p class=prompt>Find every API key or secret in this project. List which ones are safe to be public and which must stay secret. Move every secret key out of frontend code and out of any VITE_, NEXT_PUBLIC_ or REACT_APP_ variable. Create a server-side function for each call that needs a secret, store the key as a server secret, and have the frontend call that function instead.</p>
<h2>Keep checking after changes</h2>
<p>A new prompt can add a key back into the frontend without you noticing. Checking the live site after each big update catches this early. See also <a href=/guides/is-my-lovable-app-secure>Is my Lovable app secure?</a> and the <a href=/guides/supabase-rls-checklist>Supabase RLS checklist</a>.</p>"""),
"hide-api-keys-in-ai-built-apps": dict(
 title="How to hide API keys in a Lovable, Bolt, v0 or Cursor app",
 desc="Which API keys are safe in the browser, which are not, and how to move secret keys for OpenAI, Stripe and Supabase into server-side functions in apps built with AI tools.",
 body="""<p class=sub>AI app builders make it easy to connect OpenAI, Stripe or Supabase in a few prompts. The quickest way to get that working is often to put the key straight into frontend code, which means anyone who opens your site can copy it. This guide explains which keys are safe to ship, how to move the rest to the server, and what to do if a key has already been exposed.</p>
<h2>Why a key in frontend code is public</h2>
<p>Everything your app sends to the browser can be read by visitors: the HTML, the JavaScript bundle and every network request. Minifying or bundling the code does not hide anything. Keeping a key in a <code>.env</code> file does not help if frontend code reads it, because the build copies the value into the published JavaScript.</p>
<p>Build tools make this explicit with naming rules. In Vite projects, which Lovable and Bolt commonly generate, any variable starting with <code>VITE_</code> is copied into the browser bundle. In Next.js projects, which v0 generates, the same is true of variables starting with <code>NEXT_PUBLIC_</code>. Those prefixes are for values that are meant to be public. A secret key should never carry them.</p>
<h2>Which keys are meant to be public</h2>
<p>Some keys are designed to sit in the browser, and finding them in your code is not a problem on its own:</p>
<ul>
<li><b>Supabase anon or publishable key.</b> Safe in the browser, but only if Row Level Security is on. Your database rules decide what it can do. See the <a href=/guides/supabase-rls-checklist>Supabase RLS checklist</a>.</li>
<li><b>Stripe publishable key</b> (starts with <code>pk_live_</code> or <code>pk_test_</code>). It can start a checkout but cannot read payments or issue refunds.</li>
<li><b>Firebase web config and Google Maps keys.</b> These identify your project. Protect them with Firebase Security Rules and, for Google keys, restrictions to your own domain in the Google Cloud console.</li>
</ul>
<h2>Which keys must stay on the server</h2>
<ul>
<li><b>Supabase service_role or secret key.</b> It bypasses all Row Level Security.</li>
<li><b>Stripe secret and restricted keys</b> (<code>sk_live_</code>, <code>rk_live_</code>). They can read customer data and move money.</li>
<li><b>AI provider keys</b> for OpenAI, Anthropic and similar services. Anyone holding one can run requests that are billed to your account.</li>
<li><b>Email, SMS and database credentials</b>, GitHub tokens, AWS keys and any private key file.</li>
</ul>
<h2>How to move a secret key to the server</h2>
<p>The pattern is the same in every tool. The browser calls a small server-side function that you control. That function reads the key from a secret setting, calls the provider and returns only the result. The key itself never reaches the browser.</p>
<ul>
<li><b>Lovable and Bolt with Supabase:</b> use a Supabase Edge Function and store the key as a secret for that function. Both builders can create the function for you if you ask.</li>
<li><b>v0 and other Next.js apps:</b> use an API route or a Server Action, and add the key as an environment variable without the <code>NEXT_PUBLIC_</code> prefix in your Vercel project settings.</li>
<li><b>Replit:</b> store the key in Replit's Secrets tool and read it only from your server code, not from code that runs in the browser.</li>
<li><b>Cursor or any local project:</b> keep keys in a <code>.env</code> file that is listed in <code>.gitignore</code>, read them only in server code, and set the same values in your hosting provider's environment settings.</li>
</ul>
<p>Once the function exists, protect it as well. If anyone can call it without signing in, they can still use your key indirectly. Check that the user is logged in before the function does any paid work, and limit how often each user can call it.</p>
<h2>A prompt you can give your AI builder</h2>
<p class=prompt>Find every API key or secret used in my frontend code, including values read from environment variables that start with VITE_ or NEXT_PUBLIC_. For each one, tell me whether it is meant to be public. Move every secret key into a server-side function that reads it from a secret or environment variable, have the frontend call that function instead, and require a signed-in user before the function runs. List the keys you moved so I can rotate them.</p>
<h2>If a key was already exposed</h2>
<ol>
<li><b>Rotate the key first.</b> Revoke it in the provider's dashboard and create a new one. Removing it from your code is not enough, because the old key keeps working and copies of your published code may already exist.</li>
<li><b>Check your Git history.</b> If the key was ever committed, it remains in the repository's history even after you delete the file. Treat it as exposed, especially if the repository is public.</li>
<li><b>Review usage and billing.</b> Look for requests or charges you don't recognize, and set a usage limit or budget alert where the provider offers one.</li>
<li><b>Store the new key only on the server</b>, using the steps above.</li>
</ol>
<h2>Checking your live app</h2>
<p>Open your published site, open the browser developer tools and search the loaded scripts for <code>sk_live_</code>, <code>sk-</code>, <code>sk-ant-</code> and <code>service_role</code>. The free check below runs the same kind of search across your page and its script files for common secret key formats, and tells you which keys it found and how to fix them. It cannot see keys that only exist on your server, which is exactly where they should be.</p>
<p>Not sure if a key has already leaked? Read <a href=/guides/api-key-exposed-in-frontend>Is my API key exposed in my AI-built app?</a> to check your live site and learn what to do first if it has.</p>"""),
}

def render(slug):
    g = GUIDES[slug]
    body = g['body']; i = body.find('</p>') + 4  # test 2026-10-21: scan box right after the intro, plus the one at the end
    body = body[:i] + cta('guide-top') + body[i:]
    return page(f"{g['title']} | {config.APP_NAME}", f"<small class=eyebrow>GUIDE</small><h1>{E(g['title'])}</h1>{body}{cta('guide-bottom')}", desc=g["desc"])

def index():
    items = "".join(f"<div class=card><h2 style='margin-top:0'><a href=/guides/{s}>{E(g['title'])}</a></h2><p>{E(g['desc'])}</p></div>" for s, g in GUIDES.items())
    return page(f"Guides | {config.APP_NAME}", f"<h1>Guides</h1><p class=sub>Practical security and search checks for apps built with AI tools.</p>{items}{cta('guides-index')}", desc="Practical security and Google-visibility guides for apps built with Lovable, Bolt, Replit, v0 and Cursor.")

def llms_txt():
    """Plain-text summary for AI assistants (llmstxt.org format)."""
    b = config.BASE_URL
    from . import views
    lines = [f"# {config.APP_NAME}", "",
     "> A free, read-only security and Google-visibility scan for live apps built with Lovable, Bolt, Replit, v0, Cursor and Supabase. "
     "It finds exposed API keys (including Supabase service_role keys), missing security headers, unprotected pages, noindex tags, missing sitemaps and empty single-page apps, "
     "and gives a copy-paste fix prompt for each issue.", "",
     "VibeCheck Weekly only reads what a normal visitor's browser can see. It needs no code access, login or install, and it cannot read database rules directly.",
     "Pricing: the free check shows the score and the list of problems; the full report with fixes is $9 one time; weekly monitoring is $19/month for 1 app or $49/month for up to 5 apps (plus sales tax where applicable).", "",
     "## Main pages", f"- [Free scan]({b}/): paste a live URL and get results in about 30 seconds", f"- [Pricing]({b}/pricing): free check, $9 report, weekly plans", "",
     "## Guides"] + [f"- [{g['title']}]({b}/guides/{s}): {g['desc']}" for s, g in GUIDES.items()] + ["",
     "## FAQ"] + [f"- {q} {a}" for q, a in views.FAQ_LD] + ["", "## Optional", f"- [Daily tips]({b}/tips): short security and Google-visibility tips", f"- [Tips RSS]({b}/tips/rss.xml)", ""]
    return "\n".join(lines)
