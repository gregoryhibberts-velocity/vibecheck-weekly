"""Helpful SEO guide pages, each ending with a call to the free scan."""
from . import config
from .views import page, E

CTA = """<div class="card cta2"><h2>{h}</h2>
<p class=sub>Paste your live URL. The free check reads only what any visitor's browser can see and lists what is exposed and what is holding back your search visibility.</p>
<form method=post action=/scan><input type=hidden name=src value="{src}"><input type=text inputmode=url autocapitalize=off autocorrect=off spellcheck=false name=url required placeholder="myapp.lovable.app or yourdomain.com" aria-label="Your app URL">
<label class=own><input type=checkbox name=owner value=1 required> I own this app or am allowed to test it</label><button>Check my app free</button></form></div>"""
def cta(src, h="Check your app in about 30 seconds"): return CTA.replace("{src}", src).replace("{h}", h)  # test 2026-10-25 guide-bottom-cta-names-builder: guide pages pass a topic-specific heading

GUIDES = {
"is-my-lovable-app-secure": dict(
 cta_h="Check your Lovable app for these issues in about 30 seconds",
 q="How do I check if my Lovable app is secure?",
 answer="Check four things on your live app: no secret keys (such as the Supabase service_role key or an OpenAI key) in the JavaScript the browser loads, Row Level Security turned on for every Supabase table, private pages that refuse to load when you are logged out, and basic security headers. Repeat the check after big changes, because each new prompt can change your code.",
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
<p>A scan of your live site can find keys in public code, missing headers and visibility problems. It cannot see your database rules directly, so RLS should also be reviewed inside Supabase. For how this compares with Lovable's own Quick and Deep scans, see <a href=/guides/lovable-security-scan-vs-outside-scan>Lovable's security scan vs an outside scan</a>.</p>
<p>For similar checklists for other builders, see <a href=/guides/is-my-bolt-app-secure>Is my Bolt.new app secure?</a>, <a href=/guides/is-my-replit-app-secure>Is my Replit app secure?</a> and <a href=/guides/is-my-v0-app-secure>Is my v0 app secure?</a></p>"""),
"supabase-rls-checklist": dict(
 cta_h="Check your Supabase app for exposed keys in about 30 seconds",
 q="How do I set up Supabase Row Level Security correctly?",
 answer="Turn on Row Level Security for every table in the public schema, give each table separate select, insert, update and delete policies that compare the owner column with auth.uid(), use WITH CHECK on insert and update, keep the service_role key off the browser, and test by trying to read one account's data while signed in as a second account.",
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
<p>A scan of your live site cannot read your RLS policies, but it can confirm your app uses Supabase, check that no service_role key is exposed, and flag the other issues that tend to appear alongside RLS gaps.</p>
<p>Related: <a href=/guides/api-key-exposed-in-frontend>how to check if an API key is exposed in your frontend</a>, and the full <a href=/guides/is-my-lovable-app-secure>Lovable security checklist</a>.</p>"""),
"why-google-cant-find-your-ai-built-app": dict(
 cta_h="See what's keeping your app off Google in about 30 seconds",
 q="Why can't Google find my AI-built app?",
 answer="The usual causes are a leftover noindex tag, a robots.txt that blocks crawlers, no sitemap, the same title and description on every page, and pages that are empty until JavaScript runs. Fix those, then add the site to Google Search Console, submit the sitemap and request indexing for the home page.",
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
<p>Even a well-built site takes time to be crawled. Register it in Google Search Console, submit the sitemap and request indexing for the home page.</p>
<p>Security matters too before you share your link. See <a href=/guides/is-my-lovable-app-secure>Is my Lovable app secure?</a> or <a href=/guides/is-my-bolt-app-secure>Is my Bolt.new app secure?</a></p>"""),
"api-key-exposed-in-frontend": dict(
 cta_h="Check your live app for exposed keys in about 30 seconds",
 q="How do I check if my API key is exposed in my app's frontend?",
 answer="Open your live site, open the browser developer tools and search the loaded scripts for sk_live_, sk-, sk-ant- and service_role. Any secret key you find there, or stored in a variable starting with VITE_, NEXT_PUBLIC_ or REACT_APP_, is public. Rotate it at the provider first, then move the call that uses it into a server-side function.",
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
 cta_h="Check your live app for exposed keys in about 30 seconds",
 q="How do I hide API keys in a Lovable, Bolt, v0 or Cursor app?",
 answer="Keep only public keys in the browser, such as the Supabase anon key or a Stripe publishable key. Move every secret key (OpenAI, Stripe secret, Supabase service_role) into a server-side function that reads it from a secret or environment variable, have the frontend call that function, and require a signed-in user before it does any paid work.",
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
"lovable-security-scan-vs-outside-scan": dict(
 cta_h="Run the outside check on your Lovable app, free",
 q="Is Lovable's built-in security scan enough?",
 answer="Lovable's built-in scans read your project from the inside: the Quick scan checks database access rules, npm dependencies and MCP server exposure every time you publish, and the Deep scan, which you run yourself, reviews your code for access-control, injection and secret problems. An outside scan reads the live site the way a visitor does: the JavaScript and headers actually served, HTTPS, robots.txt, sitemap and whether Google can read your pages. Use Lovable's scans before you publish and an outside check of the live URL after, especially if you use a custom domain or care about search traffic.",
 title="Lovable's security scan vs an outside scan: what each one checks",
 desc="A plain comparison of Lovable's built-in Quick and Deep security scans and an outside scan of your live app: what each can see, what each misses, and when to use both.",
 updated="2026-10-22",
 body="""<p class=sub>Lovable now includes its own security scans, and they are worth running. They look at your project from the inside. An outside scan looks at the published app from the outside, the way any visitor or attacker would. The two answer different questions, so here is what each one covers.</p>
<h2>What Lovable's built-in scans check</h2>
<p>According to <a href="https://docs.lovable.dev/features/security" rel=nofollow>Lovable's security documentation</a>, there are two scans:</p>
<ul>
<li><b>Quick scan</b> runs automatically when you open the publish dialog. It reviews your database access rules (for example tables without Row Level Security, or rules that let everyone through), checks your npm dependencies for known critical vulnerabilities, and flags an MCP server exposed without sign-in.</li>
<li><b>Deep scan</b> reviews your application code for access-control mistakes, endpoints anyone can call, unsafe input, secrets in source code, payment logic a customer could change, and weak sign-in or recovery flows. It does not run automatically as you work: you start it from the Security view. Scheduled deep scans are an Enterprise feature.</li>
</ul>
<p>Lovable's documentation also says plainly that these tools cannot guarantee complete security and recommends a further review for apps that handle sensitive data.</p>
<h2>What an outside scan checks</h2>
<p>An outside scan never sees your code or your database. It loads your live URL and checks what is actually being served:</p>
<ul>
<li>Secret keys, such as a Supabase service_role key, inside the JavaScript files the browser downloads</li>
<li>Security headers on the real responses, HTTPS, and whether plain HTTP redirects to HTTPS</li>
<li>Google visibility: page title, meta description, social preview tags, robots.txt, sitemap.xml, and whether the page has readable text before JavaScript runs</li>
</ul>
<h2>Side by side</h2>
<table class=cmp><tr><th></th><th>Lovable Quick and Deep scans</th><th>Outside scan of the live site</th></tr>
<tr><td>Looks at</td><td>Your project code, database rules and dependencies</td><td>The published pages, scripts and headers</td></tr>
<tr><td>Row Level Security</td><td>Yes, reviews the rules directly</td><td>No, it cannot see database rules</td></tr>
<tr><td>Keys in shipped JavaScript</td><td>Deep scan looks for secrets in source code</td><td>Yes, searches the files visitors actually download</td></tr>
<tr><td>Security headers and HTTPS</td><td>Not listed in the scan coverage</td><td>Yes</td></tr>
<tr><td>Google visibility</td><td>Not a security scan topic</td><td>Yes: titles, descriptions, robots.txt, sitemap, readable HTML</td></tr>
<tr><td>Custom domains and other hosts</td><td>Lovable projects only</td><td>Any live URL, whatever tool built it</td></tr>
<tr><td>When it runs</td><td>Quick scan at publish; Deep scan when you start it</td><td>Whenever you run it, or on a weekly schedule</td></tr></table>
<h2>When to use which</h2>
<p>Run Lovable's Quick scan and a Deep scan before you publish, and fix what they find. Then check the live URL from the outside, because that is what your users and Google actually receive. Repeat the outside check after big changes, since each new prompt can change what gets shipped. If your app moved off Lovable, or was built with Bolt, Replit, v0 or Cursor, the outside check works the same way. For Bolt's own built-in checks, see <a href=/guides/is-my-bolt-app-secure>Is my Bolt.new app secure?</a></p>
<p>For the inside checks in more detail, see <a href=/guides/is-my-lovable-app-secure>Is my Lovable app secure?</a> and the <a href=/guides/supabase-rls-checklist>Supabase RLS checklist</a>.</p>"""),
"is-my-bolt-app-secure": dict(
 cta_h="Check your Bolt app for these issues in about 30 seconds",
 q="How do I check if my Bolt.new app is secure?",
 answer="Run Bolt's own checks first: the Security Audit page in your database settings (all plans) flags missing Row Level Security and policies that are too open, and Run security audit in the Publish menu (paid plans) reviews your whole project. Then check the live site from the outside: search the JavaScript it serves for secret keys such as sk_live_ or service_role, open private pages while logged out, and confirm security headers, HTTPS, robots.txt and a sitemap are in place.",
 title="Is my Bolt.new app secure? A pre-launch checklist",
 desc="How to check an app built with Bolt.new for security problems: what Bolt's database Security Audit and project security audit cover, and the checks to run on your published site.",
 updated="2026-10-23",
 body="""<p class=sub>Bolt.new can take an app from a prompt to a published site with a database, sign-in and payments in an afternoon. Bolt now includes its own security checks, and they are the right place to start. This guide explains what each one covers and which checks are still worth running on the live site.</p>
<h2>1. Run Bolt's database Security Audit (all plans)</h2>
<p>If your project uses a Bolt Cloud database, open the database icon at the top of the editor and choose <b>Security</b>. According to <a href="https://support.bolt.new/cloud/database/security" rel=nofollow>Bolt's documentation</a>, this page uses the same checks as Supabase's Security Advisor. It flags problems such as tables without Row Level Security, a policy that always returns true, and leaked-password protection being turned off. <b>Ask Bolt to fix</b> sends the findings back to Bolt. It checks the database only, not your code, so open it again after every database change.</p>
<h2>2. Run the project security audit before you publish (paid plans)</h2>
<p>In the <b>Publish</b> menu, <b>Run security audit</b> reviews the whole project, code and database together. <a href="https://support.bolt.new/building/security" rel=nofollow>Bolt says</a> it looks at who can see and change data, what error messages and sign-in screens reveal, how sign-in and sign-out work, ways users could change a price or skip a step, unchecked input, and private keys stored in code or sent to the browser. Bolt fixes most issues itself and lists anything you need to change by hand, such as a setting in your email or payment provider. Using this button does not use tokens; asking Bolt to audit the project in chat does.</p>
<h2>3. Check the live site for secret keys</h2>
<p>Bolt projects are usually Vite apps, and any environment variable that starts with <code>VITE_</code> is copied into the JavaScript every visitor downloads. Open your published site, open the browser developer tools and search the loaded scripts for <code>sk_live_</code>, <code>sk-</code>, <code>sk-ant-</code> and <code>service_role</code>. The Supabase anon key and a Stripe publishable key (<code>pk_live_</code>) are meant to be public; secret keys are not. If you find one, rotate it at the provider first, then move the call into a server function and store the key in Bolt's Secrets settings. See <a href=/guides/hide-api-keys-in-ai-built-apps>how to hide API keys in a Lovable, Bolt, v0 or Cursor app</a>.</p>
<h2>4. Test private pages while logged out</h2>
<p>Open a private browser window and go straight to your dashboard, admin and account URLs, and any URL with a record ID in it. If data loads without signing in, or changing the ID shows someone else's record, the data is not protected on the server. Repeat the test signed in as a second account.</p>
<h2>5. Check headers, HTTPS and file storage</h2>
<p>Confirm the site redirects http:// to https:// and sends basic security headers such as Content-Security-Policy, X-Content-Type-Options and a frame policy. In the database settings, check which file storage buckets are public. A bucket marked public can be read by anyone who has a file's link.</p>
<h2>6. Make sure Google can find it</h2>
<p>Security is only half of a launch. View your page source and search for "noindex", visit /robots.txt and /sitemap.xml on your real domain, and give each page its own title and description. A Vite app often sends almost no text in its HTML until JavaScript runs, which makes it harder for search engines to read. <a href=/guides/why-google-cant-find-your-ai-built-app>Why Google can't find your AI-built app</a> covers the fixes.</p>
<h2>Bolt's checks and an outside check, side by side</h2>
<table class=cmp><tr><th></th><th>Bolt's Security Audit and project audit</th><th>Outside check of the live site</th></tr>
<tr><td>Looks at</td><td>Your project code and Bolt database</td><td>The published pages, scripts and headers</td></tr>
<tr><td>Row Level Security and policies</td><td>Yes</td><td>No, it cannot see database rules</td></tr>
<tr><td>Keys sent to the browser</td><td>Project audit checks code for this</td><td>Yes, searches the files visitors actually download</td></tr>
<tr><td>Security headers and HTTPS</td><td>Not listed in Bolt's audit coverage</td><td>Yes</td></tr>
<tr><td>Google visibility</td><td>Not part of the audit</td><td>Yes: noindex, titles, robots.txt, sitemap, readable HTML</td></tr>
<tr><td>Cost</td><td>Database check on all plans; project audit on paid plans</td><td>Free first check</td></tr></table>
<h2>A prompt you can give Bolt</h2>
<p class=prompt>Review this project for security before launch. Make sure Row Level Security is on for every table with separate select, insert, update and delete policies limited to the signed-in user. Move every secret key out of frontend code and out of any VITE_ variable into a server function that reads it from Secrets. Make every dashboard, admin and account page and every server function require a signed-in user, and check on the server that the user owns the record they ask for. List anything I need to change by hand.</p>
<p>For the Supabase side in more detail, see the <a href=/guides/supabase-rls-checklist>Supabase RLS checklist</a>. Building with Replit instead? See <a href=/guides/is-my-replit-app-secure>Is my Replit app secure?</a></p>"""),
"is-my-replit-app-secure": dict(
 cta_h="Check your Replit app for these issues in about 30 seconds",
 q="How do I check if my Replit app is secure?",
 answer="Start with Replit's Security Center: the free Level 1 scan and automatic dependency scans check your packages for known vulnerabilities, and on paid plans the Level 2 deep scan reviews your code and Level 3 also tests the running Preview. Turn on Block publishing of critical vulnerabilities. Then check the published app from the outside: search the JavaScript it serves for secret keys, open private pages and API routes while logged out, and confirm HTTPS, security headers, robots.txt and a sitemap on your real domain.",
 title="Is my Replit app secure? What Replit's Security Center checks and what to test yourself",
 desc="How to check an app built with Replit Agent for security problems: what Replit's scan levels, publish checks and Auto-Protect cover, and the checks to run on your published app.",
 updated="2026-10-24",
 body="""<p class=sub>Replit Agent can build and publish a full-stack app, with a server, database and sign-in, from a single prompt. Replit now has several built-in security checks, and they are the right place to start. This guide explains what each one covers, what none of them can promise, and the checks worth running on the live app yourself.</p>
<h2>1. Know what Replit checks for you</h2>
<p>According to <a href="https://docs.replit.com/features/security/security-scan-levels" rel=nofollow>Replit's documentation</a>, the Security Center (in the Tools pane) offers three scan levels:</p>
<ul>
<li><b>Level 1, basic security checks (free):</b> checks your packages against known vulnerabilities. It does not review your own code.</li>
<li><b>Level 2, deep security scan (paid plans):</b> adds a Security Agent review of your source code, combining AI review with static analysis tools such as Semgrep. It looks for problems like SQL injection, cross-site scripting and sensitive data written to logs.</li>
<li><b>Level 3, AI pentest:</b> adds an outside test of your running Preview through the browser and network. It has extra plan and access requirements.</li>
</ul>
<p>Replit also scans your dependencies automatically when new vulnerabilities are published, reviews files the Agent changes for hardcoded secrets as you build, and runs a check before every publish. Replit's own docs say a passing publish check does not mean your code has no vulnerabilities, and that no scan guarantees an app is secure.</p>
<h2>2. Check two settings</h2>
<p>In the Publishing tool, under Adjust settings, make sure <b>Block publishing of critical vulnerabilities</b> is on. When it is off, a critical finding is only listed and the publish goes ahead. If you want Replit to prepare patches for vulnerable packages, a workspace admin can turn on <b>Auto-Protect</b> in Settings, and you can choose which severity triggers an email. Both Auto-Protect settings are off by default. After applying any fix, republish: the published app keeps running the old version until you do.</p>
<h2>3. Keep secret keys in Secrets, and out of the browser</h2>
<p>Store API keys in Replit's <b>Secrets</b> tool and read them only in server code. Secrets sync to the published app when you publish. A key stored in Secrets can still leak if frontend code uses it: in a Vite frontend, any variable starting with <code>VITE_</code> is copied into the JavaScript every visitor downloads. Open your published app, open the browser developer tools and search the loaded scripts for <code>sk_live_</code>, <code>sk-</code>, <code>sk-ant-</code> and <code>service_role</code>. If you find one, rotate it at the provider first, then move the call to your server. Our guide on <a href=/guides/hide-api-keys-in-ai-built-apps>how to hide API keys</a> shows the pattern.</p>
<h2>4. Test private pages and API routes while logged out</h2>
<p>Replit apps usually have their own server, such as Express or Flask, so access control lives in your route code. Open a private browser window and go straight to dashboard, admin and account pages, and to API routes like <code>/api/users</code> or any URL with a record ID. If data comes back without signing in, or changing an ID shows another user's record, the route is not checking who is asking. Repeat the test signed in as a second account. Hiding a button in the interface does not protect the route behind it.</p>
<h2>5. Check the published app, not only the Preview</h2>
<p>Level 3 tests the running Preview. Your users get the published app, often on a custom domain. Confirm that http:// redirects to https://, that basic security headers such as Content-Security-Policy, X-Content-Type-Options and a frame policy are sent, and that error pages don't show stack traces or file paths. Also check which access option you chose when publishing (Public, Password protected or Invite only) so an internal tool isn't public by accident.</p>
<h2>6. Make sure Google can find it</h2>
<p>Security scans don't cover search visibility. Visit /robots.txt and /sitemap.xml on your real domain, give each page its own title and description, and view your page source to make sure your main text is in the HTML. Also check that Google is indexing your custom domain rather than the <code>.replit.app</code> address. <a href=/guides/why-google-cant-find-your-ai-built-app>Why Google can't find your AI-built app</a> covers the fixes.</p>
<h2>Replit's checks and an outside check, side by side</h2>
<table class=cmp><tr><th></th><th>Replit Security Center and publish checks</th><th>Outside check of the published app</th></tr>
<tr><td>Looks at</td><td>Your packages and source code; Level 3 also tests the running Preview</td><td>The published pages, scripts and headers on your real domain</td></tr>
<tr><td>Vulnerable packages</td><td>Yes, free and automatic</td><td>No</td></tr>
<tr><td>Code problems such as SQL injection</td><td>Level 2 and 3 (paid plans)</td><td>No, it cannot see your code</td></tr>
<tr><td>Keys sent to the browser</td><td>Flags hardcoded secrets in code</td><td>Yes, searches the files visitors actually download</td></tr>
<tr><td>Security headers and HTTPS on your domain</td><td>Not on your published domain (Level 3 tests the Preview)</td><td>Yes</td></tr>
<tr><td>Google visibility</td><td>Not part of the scans</td><td>Yes: noindex, titles, robots.txt, sitemap, readable HTML</td></tr></table>
<h2>A prompt you can give Replit Agent</h2>
<p class=prompt>Review this app for security before I publish. Make sure every secret key is read from Secrets only in server code and never sent to the browser or stored in a VITE_ variable. Make every dashboard, admin and account page and every API route require a signed-in user, and check on the server that the user owns the record they ask for. Add security headers (Content-Security-Policy, X-Content-Type-Options, Referrer-Policy and a frame policy), hide stack traces in production errors, and add a robots.txt and sitemap.xml. List anything I need to change by hand.</p>
<p>For similar checklists for other builders, see <a href=/guides/is-my-lovable-app-secure>Is my Lovable app secure?</a>, <a href=/guides/is-my-bolt-app-secure>Is my Bolt.new app secure?</a> and <a href=/guides/is-my-v0-app-secure>Is my v0 app secure?</a></p>"""),
"is-my-v0-app-secure": dict(
 q="How do I check if my v0 app is secure?",
 answer="v0 builds Next.js apps, so start with environment variables: anything named NEXT_PUBLIC_ is copied into the JavaScript every visitor downloads, so secret keys (Supabase service_role or sb_secret_, Stripe sk_live_, OpenAI or Anthropic keys) must never use that prefix and should be stored as Secret variables in Vercel. Then turn on Row Level Security for every Supabase table, make every route handler and server action check the signed-in user and record owner, open private pages while logged out, and confirm security headers, robots.txt and a sitemap on your live domain.",
 title="Is my v0 app secure? A checklist for Next.js apps built with v0",
 desc="How to check an app built with v0 by Vercel for exposed NEXT_PUBLIC_ keys, Supabase Row Level Security gaps, unprotected server actions and missing headers before launch.",
 updated="2026-10-25",
 cta_h="Check your v0 app for these issues in about 30 seconds",
 body="""<p class=sub>v0 turns a prompt into a working Next.js app and deploys it to Vercel in one click. The code it writes is a good start, but who can see which data is still up to you. These are the checks worth doing before you share the link.</p>
<h2>1. Check every NEXT_PUBLIC_ variable</h2>
<p>In a Next.js app, any environment variable whose name starts with <code>NEXT_PUBLIC_</code> is written into the JavaScript sent to the browser when the app is built. Variables without the prefix stay on the server. <a href="https://v0.app/docs/security" rel=nofollow>v0's security docs</a> say it watches for risky <code>NEXT_PUBLIC_</code> use and warns you, but it is still worth looking yourself.</p>
<p><b>How to check:</b> in Vercel, open your project, then Settings and Environment Variables, and read every name that starts with <code>NEXT_PUBLIC_</code>. The Supabase project URL, the Supabase anon or publishable key and a Stripe publishable key (<code>pk_live_</code>) are meant to be public. A Supabase <code>service_role</code> or <code>sb_secret_</code> key, a Stripe <code>sk_live_</code> key, or an OpenAI or Anthropic key is not. If one has the prefix, rotate it at the provider first, rename it without the prefix, read it only in server code, and redeploy, because existing deployments keep the old values.</p>
<h2>2. Store secrets as Secret variables</h2>
<p>Vercel lets you save a variable as a Secret, which cannot be read back in the dashboard after saving. Use that for passwords, API keys and tokens. If a key was saved as a readable value by mistake, delete it, add it again as a Secret and rotate the key. See <a href=/guides/hide-api-keys-in-ai-built-apps>how to hide API keys in a Lovable, Bolt, v0 or Cursor app</a>.</p>
<h2>3. Turn on Row Level Security in Supabase</h2>
<p>When a v0 app uses Supabase, client components often query the database straight from the browser with the public key. That is only safe when Row Level Security is on for every table and the policies limit each user to their own rows. Supabase's Security Advisor flags tables without it. The <a href=/guides/supabase-rls-checklist>Supabase RLS checklist</a> walks through the policies.</p>
<h2>4. Protect route handlers and server actions</h2>
<p>Route handlers and server actions run on the server, but anyone can call them directly, not just your buttons. Each one that reads or changes data should check who is signed in and that the record belongs to them. Hiding a button in a client component does not protect the action behind it.</p>
<p><b>How to check:</b> open a private browser window and go straight to your dashboard, admin and account URLs, and to any URL with a record ID in it. Then sign in as a second account and try the first account's IDs. Data should not load in either case.</p>
<h2>5. Check preview links, headers and HTTPS</h2>
<p>Each change can create a new preview deployment with its own vercel.app link. In Vercel, Settings and Deployment Protection controls whether those links need a Vercel sign-in, so check it is on if previews use real data. On your production domain, confirm basic security headers such as Content-Security-Policy, X-Content-Type-Options, Referrer-Policy and a frame policy. Next.js does not add most of these unless you set them in <code>next.config</code> or middleware.</p>
<h2>6. Make sure Google can find it</h2>
<p>View the page source of your live site and search for "noindex", visit /robots.txt and /sitemap.xml on your real domain, and give each page its own title and description through Next.js metadata. Pages built only from client components can send little readable text before JavaScript runs. <a href=/guides/why-google-cant-find-your-ai-built-app>Why Google can't find your AI-built app</a> covers the fixes.</p>
<h2>v0's built-in protection and an outside check, side by side</h2>
<table class=cmp><tr><th></th><th>v0 and Vercel</th><th>Outside check of the live site</th></tr>
<tr><td>Looks at</td><td>Your code while v0 writes it, and your Vercel settings</td><td>The published pages, scripts and headers</td></tr>
<tr><td>Secret keys in NEXT_PUBLIC_ variables</td><td>v0 warns about risky use</td><td>Yes, searches the files visitors actually download</td></tr>
<tr><td>Row Level Security and policies</td><td>No, set in Supabase</td><td>No, it cannot see database rules</td></tr>
<tr><td>Security headers and HTTPS</td><td>HTTPS by default; headers are up to you</td><td>Yes</td></tr>
<tr><td>Google visibility</td><td>Up to your metadata and sitemap</td><td>Yes: noindex, titles, robots.txt, sitemap, readable HTML</td></tr></table>
<h2>A prompt you can give v0</h2>
<p class=prompt>Review this app for security before launch. Make sure no secret key uses a NEXT_PUBLIC_ name and that secret keys are read only in server code that client components never import. Make every route handler and server action that reads or changes data check the signed-in user on the server and confirm they own the record. If the app uses Supabase, list every table and the Row Level Security policies it needs so users can only reach their own rows. Add security headers (Content-Security-Policy, X-Content-Type-Options, Referrer-Policy and a frame policy) in next.config, and add a robots.txt, a sitemap and a title and description for each page. List anything I need to change by hand in Vercel or Supabase.</p>
<p>For similar checklists for other builders, see <a href=/guides/is-my-lovable-app-secure>Is my Lovable app secure?</a>, <a href=/guides/is-my-bolt-app-secure>Is my Bolt.new app secure?</a> and <a href=/guides/is-my-replit-app-secure>Is my Replit app secure?</a></p>"""),
}
def head(slug, g):
    """Canonical, social preview tags and structured data so search engines and AI assistants can cite the guide."""
    import json
    b = config.BASE_URL; url = f"{b}/guides/{slug}"
    ld = lambda o: "<script type='application/ld+json'>" + json.dumps(o).replace("<", "\\u003c") + "</script>"
    art = {"@context": "https://schema.org", "@type": "TechArticle", "headline": g["title"], "description": g["desc"], "url": url,
           "mainEntityOfPage": url, "inLanguage": "en", "dateModified": g.get("updated", "2026-10-21"),
           "author": {"@type": "Organization", "name": config.APP_NAME, "url": b + "/"},
           "publisher": {"@type": "Organization", "name": config.APP_NAME, "url": b + "/"}}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": config.APP_NAME, "item": b + "/"},
        {"@type": "ListItem", "position": 2, "name": "Guides", "item": b + "/guides"},
        {"@type": "ListItem", "position": 3, "name": g["title"], "item": url}]}
    out = (f"<link rel=canonical href='{url}'><meta property='og:type' content='article'><meta property='og:url' content='{url}'>"
           f"<meta property='og:title' content='{E(g['title'])}'><meta property='og:description' content='{E(g['desc'])}'>"
           + ld(art) + ld(crumbs))
    if g.get("answer"):
        out += ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": g.get("q") or g["title"],
                   "acceptedAnswer": {"@type": "Answer", "text": g["answer"]}}]})
    return out

def render(slug):
    g = GUIDES[slug]
    body = g['body']; i = body.find('</p>') + 4  # test 2026-10-21: scan box right after the intro, plus the one at the end
    short = f"<div class='card short'><b>Short answer</b><p style='margin:.4em 0 0'>{E(g['answer'])}</p></div>" if g.get("answer") else ""
    body = body[:i] + short + cta('guide-top') + body[i:]
    return page(f"{g['title']} | {config.APP_NAME}", f"<small class=eyebrow>GUIDE</small><h1>{E(g['title'])}</h1>{body}{cta('guide-bottom', g.get('cta_h') or 'Check your app in about 30 seconds')}", extra_head=head(slug, g), desc=g["desc"])

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
     "## Guides"] + [f"- [{g['title']}]({b}/guides/{s}): {g.get('answer') or g['desc']}" for s, g in GUIDES.items()] + ["",
     "## FAQ"] + [f"- {q} {a}" for q, a in views.FAQ_LD] + ["", "## Optional", f"- [Daily tips]({b}/tips): short security and Google-visibility tips", f"- [Tips RSS]({b}/tips/rss.xml)", ""]
    return "\n".join(lines)
