import sys
from playwright.sync_api import sync_playwright
B = "https://vibecheck-weekly.vercel.app"; site = open("/workspace/agent-tools/live_site.txt").read().strip(); S = "/workspace/appcheck/shots/"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]); pg = b.new_page(viewport={"width": 1280, "height": 900})
    pg.goto(B + "/"); pg.screenshot(path=S + "live-landing.png", full_page=True)
    pg.goto(B + "/pricing"); pg.screenshot(path=S + "live-pricing.png", full_page=True)
    pg.goto(site); pg.screenshot(path=S + "live-verify.png", full_page=True)
    pg.click("text=Verify and run my free check"); pg.wait_for_load_state("networkidle", timeout=90000)
    print("after verify:", pg.url); pg.screenshot(path=S + "live-report.png", full_page=True)
    print("report has OpenAI finding:", "OpenAI API key" in pg.content())
    pg.goto(site); pg.screenshot(path=S + "live-site-verified.png", full_page=True)
    pg.click("text=Monitor 1 app"); pg.wait_for_load_state("load")
    print("checkout click ->", pg.url, "|", pg.inner_text("h1")); pg.screenshot(path=S + "live-checkout-unconfigured.png", full_page=True)
    b.close()
