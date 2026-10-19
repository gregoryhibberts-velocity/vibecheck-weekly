from playwright.sync_api import sync_playwright
url = open("/workspace/agent-tools/cs_url.txt").read().strip(); S = "/workspace/appcheck/shots/"
site = open("/workspace/agent-tools/live_site.txt").read().strip()
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); pg = b.new_page(viewport={"width": 1024, "height": 800})
    pg.goto(url); pg.wait_for_timeout(6000); pg.mouse.click(629, 424); pg.wait_for_selector("#cardNumber", timeout=30000)
    pg.fill("#cardNumber", "4242424242424242"); pg.fill("#cardExpiry", "12/34"); pg.fill("#cardCvc", "123"); pg.fill("#billingName", "Test Buyer")
    if pg.locator("#billingCountry").count(): pg.select_option("#billingCountry", "US")
    pg.fill("#billingAddressLine1", "1 Test St"); pg.fill("#billingLocality", "Chicago"); pg.fill("#billingPostalCode", "60601")
    if pg.locator("#billingAdministrativeArea").count(): pg.select_option("#billingAdministrativeArea", "IL")
    if pg.locator("#enableStripePass").count() and pg.locator("#enableStripePass").is_checked(): pg.uncheck("#enableStripePass")
    pg.wait_for_timeout(2000); pg.screenshot(path=S + "live-stripe-checkout.png", full_page=True)
    pg.get_by_role("button", name="Subscribe").click()
    try: pg.wait_for_url("**/billing/success**", timeout=90000)
    except Exception as e: pg.screenshot(path="/tmp/cs_fail.png", full_page=True); raise
    pg.screenshot(path=S + "live-payment-success.png", full_page=True)
    pg.wait_for_timeout(6000); pg.goto(site); c = pg.content()
    print("Pro shown:", "<b>Pro</b>" in c, "| weekly on:", "Weekly monitoring: <b>on" in c)
    pg.screenshot(path=S + "live-site-pro.png", full_page=True); b.close()
