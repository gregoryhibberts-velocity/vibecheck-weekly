"""Helpful SEO guide pages, each ending with a call to the free scan."""
from . import config
from .views import page, E

CTA = """<div class="card cta2"><h2>Check your app in about 30 seconds</h2>
<p class=sub>Paste your live URL. The free check reads only what any visitor's browser can see and lists what is exposed and what is holding back your search visibility.</p>
<form method=post action=/scan><input type=url name=url required placeholder="https://myapp.lovable.app" aria-label="Your app URL">
<label class=own><input type=checkbox name=owner value=1 required> I own this app or am allowed to test it</label><button>Check my app free</button></form></div>"""

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
}

def render(slug):
    g = GUIDES[slug]
    return page(f"{g['title']} | {config.APP_NAME}", f"<small class=eyebrow>GUIDE</small><h1>{E(g['title'])}</h1>{g['body']}{CTA}", desc=g["desc"])

def index():
    items = "".join(f"<div class=card><h2 style='margin-top:0'><a href=/guides/{s}>{E(g['title'])}</a></h2><p>{E(g['desc'])}</p></div>" for s, g in GUIDES.items())
    return page(f"Guides | {config.APP_NAME}", f"<h1>Guides</h1><p class=sub>Practical security and search checks for apps built with AI tools.</p>{items}{CTA}", desc="Practical security and Google-visibility guides for apps built with Lovable, Bolt, Replit, v0 and Cursor.")
