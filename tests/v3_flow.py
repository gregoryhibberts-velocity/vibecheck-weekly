import sys, re
from playwright.sync_api import sync_playwright
B = "https://vibecheck-weekly.vercel.app"; S = "/workspace/appcheck/shots/v3-"; T = "https://vibecheck-testpage.vercel.app/"
def pay(pg, name):
    pg.wait_for_url("https://checkout.stripe.com/**", timeout=60000); pg.wait_for_timeout(6000); pg.screenshot(path="/tmp/payload.png"); print("on stripe", flush=True)
    if not pg.locator("#cardNumber").is_visible(): pg.mouse.click(629, 424)
    pg.wait_for_selector("#cardNumber", timeout=30000)
    pg.fill("#cardNumber", "4242424242424242"); pg.fill("#cardExpiry", "12/34"); pg.fill("#cardCvc", "123"); pg.fill("#billingName", "Test Buyer")
    if pg.locator("#billingCountry").count(): pg.select_option("#billingCountry", "US")
    for sel, v in (("#billingAddressLine1", "1 Test St"), ("#billingLocality", "Chicago"), ("#billingPostalCode", "60601")):
        if pg.locator(sel).count(): pg.fill(sel, v)
    if pg.locator("#billingAdministrativeArea").count(): pg.select_option("#billingAdministrativeArea", "IL")
    if pg.locator("#enableStripePass").count() and pg.locator("#enableStripePass").is_checked(): pg.uncheck("#enableStripePass")
    pg.wait_for_timeout(1500); pg.screenshot(path=S + name, full_page=True)
    pg.locator("button[type=submit]").first.click(); print("submitted", flush=True)
    try: pg.wait_for_url(B + "/**", timeout=90000)
    except Exception: pg.screenshot(path="/tmp/payfail.png", full_page=True); raise
    pg.wait_for_load_state("networkidle")
step = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); pg = b.new_page(viewport={"width": 1024, "height": 800})
    if step == "a":
        pg.goto(B + "/"); pg.screenshot(path=S + "landing.png", full_page=True)
        pg.fill("form.cta input[name=url]", T); pg.check("form.cta input[name=owner]"); pg.click("form.cta button"); pg.wait_for_url("**/r/**", timeout=90000)
        rep = pg.url; pg.screenshot(path=S + "teaser.png", full_page=True)
        pg.fill("input[name=email]", "test+v3@example.com"); pg.click("form.lock button"); pg.wait_for_load_state("networkidle")
        print("titles mode:", "Unlock full report" in pg.content()); pg.screenshot(path=S + "email-gate-results.png", full_page=True)
        pg.click("text=Unlock full report – $9"); pg.wait_for_load_state("load")
        if "checkout.stripe.com" not in pg.url: print("UNLOCK BUTTON FAILED:", pg.url, pg.inner_text("h1")); pg.screenshot(path=S + "unlock-fail.png"); sys.exit(1)
        pay(pg, "stripe-unlock.png"); print("after unlock url:", pg.url, "| full report:", "Paste into your AI tool" in pg.content())
        pg.screenshot(path=S + "full-report.png", full_page=True)
        pg.click("text=Monitor weekly from $19/mo"); pg.wait_for_url("**/site/**"); site = pg.url; open("/workspace/agent-tools/v3_site.txt", "w").write(site)
        open("/workspace/agent-tools/v3_token.txt", "w").write(re.search(r"vcw-[0-9a-f]{24}", pg.content()).group(0)); pg.screenshot(path=S + "verify.png", full_page=True); print("site saved")
    elif step == "b":
        site = open("/workspace/agent-tools/v3_site.txt").read().strip(); pg.goto(site)
        pg.click("text=Verify and run my free check"); pg.wait_for_load_state("networkidle"); print("after verify:", pg.url)
        pg.goto(site); pg.screenshot(path=S + "site-verified.png", full_page=True)
        pg.click("text=Monitor 1 app"); pg.wait_for_load_state("load")
        if "checkout.stripe.com" not in pg.url: print("MONTHLY BUTTON FAILED:", pg.url); sys.exit(1)
        pay(pg, "stripe-monthly.png"); print("thanks page:", pg.url, "|", pg.inner_text("h1")); pg.screenshot(path=S + "thanks.png", full_page=True)
        pg.wait_for_timeout(4000); pg.goto(site); c = pg.content()
        print("Solo:", "<b>Solo</b>" in c, "| weekly on:", "Weekly monitoring: <b>on" in c); pg.screenshot(path=S + "site-subscribed.png", full_page=True)
    elif step == "1":
        pg.goto(B + "/"); pg.screenshot(path=S + "landing.png", full_page=True)
        pg.fill("form.cta input[name=url]", T); pg.check("form.cta input[name=owner]"); pg.click("form.cta button"); pg.wait_for_url("**/r/**", timeout=90000)
        rep = pg.url; open("/workspace/agent-tools/v2_report.txt", "w").write(rep); pg.screenshot(path=S + "teaser.png", full_page=True)
        pg.fill("input[name=email]", "test+v2@example.com"); pg.click("form.lock button"); pg.wait_for_load_state("networkidle")
        print("titles mode:", "Unlock full report" in pg.content(), "| fix prompts hidden:", "Paste into your AI tool" not in pg.content()); pg.screenshot(path=S + "email-gate-results.png", full_page=True)
        pg.click("text=Unlock full report – $9"); pg.wait_for_load_state("load")
        print("site unlock button ->", pg.url, "|", pg.inner_text("h1")); pg.screenshot(path=S + "unlock-button-result.png", full_page=True)
        pg.goto(rep); pg.click("text=Or monitor weekly from $19/mo"); pg.wait_for_url("**/site/**"); site = pg.url; open("/workspace/agent-tools/v2_site.txt", "w").write(site)
        tok = re.search(r"vcw-[0-9a-f]{24}", pg.content()).group(0); open("/workspace/agent-tools/v2_token.txt", "w").write(tok)
        pg.screenshot(path=S + "verify.png", full_page=True); print("site:", site, "token saved")
    elif step == "pay":
        pg.goto(sys.argv[2]); pay(pg, sys.argv[3]); print("landed:", pg.url)
        c = pg.content(); print("full report:", "Paste into your AI tool" in c, "| Solo:", "<b>Solo</b>" in c, "| weekly on:", "Weekly monitoring: <b>on" in c)
        pg.screenshot(path=S + sys.argv[4], full_page=True)
    elif step == "verify":
        site = open("/workspace/agent-tools/v2_site.txt").read().strip(); pg.goto(site)
        pg.click("text=Verify and run my free check"); pg.wait_for_load_state("networkidle"); print("after verify:", pg.url)
        pg.goto(site); pg.screenshot(path=S + "site-verified.png", full_page=True)
        pg.click("text=Monitor 1 app"); pg.wait_for_load_state("load"); print("site monthly button ->", pg.url, "|", pg.inner_text("h1"))
        pg.screenshot(path=S + "monthly-button-result.png", full_page=True)
    else:
        site = open("/workspace/agent-tools/v2_site.txt").read().strip(); pg.goto(site)
        pg.click("text=Verify and run my free check"); pg.wait_for_load_state("networkidle"); print("after verify:", pg.url)
        pg.goto(site); pg.screenshot(path=S + "site-verified.png", full_page=True)
        pg.click("text=Monitor 1 app"); pay(pg, "stripe-monthly.png"); pg.screenshot(path=S + "payment-success.png", full_page=True)
        pg.wait_for_timeout(5000); pg.goto(site); c = pg.content()
        print("Solo plan:", "<b>Solo</b>" in c, "| weekly on:", "Weekly monitoring: <b>on" in c); pg.screenshot(path=S + "site-subscribed.png", full_page=True)
    b.close()
