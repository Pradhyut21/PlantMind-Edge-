import os
import time
from playwright.sync_api import sync_playwright

output_dir = os.path.abspath("./docs/screenshots")
os.makedirs(output_dir, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    # Set high-DPI viewport (1440x960) for ultra-crisp screenshots
    context = browser.new_context(viewport={'width': 1440, 'height': 960}, device_scale_factor=2)
    page = context.new_page()

    print("[1/5] Capturing 01_offline_search.png...")
    page.goto('http://localhost:3000')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    # Click Airplane Mode toggle if not already offline
    airplane_btn = page.locator("button:has-text('ONLINE (LAN)')")
    if airplane_btn.count() > 0:
        airplane_btn.first.click()
        time.sleep(0.5)

    # Perform search and press Enter
    search_input = page.locator("input[placeholder*='Search fault symptoms']")
    search_input.fill("hydraulic pressure keeps dropping on line 3 press")
    search_input.press("Enter")
    time.sleep(2)

    page.screenshot(path=os.path.join(output_dir, "01_offline_search.png"), full_page=False)

    print("[2/5] Capturing 02_append_only_write.png...")
    # Click Log Observation tab
    page.locator("button:has-text('Log Observation')").first.click()
    time.sleep(0.5)
    # Click Relief Valve Tip demo filler
    page.locator("button:has-text('+ Relief Valve Tip')").first.click()
    time.sleep(0.5)
    page.screenshot(path=os.path.join(output_dir, "02_append_only_write.png"), full_page=False)

    print("[3/5] Capturing 03_device_memory_inspector.png...")
    # Click Device Memory Inspector tab
    page.locator("button:has-text('Device Memory Inspector')").first.click()
    time.sleep(1)
    page.screenshot(path=os.path.join(output_dir, "03_device_memory_inspector.png"), full_page=False)

    print("[4/5] Capturing 04_conflict_reconciliation.png...")
    # Switch to Central Office view
    page.locator("button:has-text('Central Office')").first.click()
    time.sleep(1.5)
    page.screenshot(path=os.path.join(output_dir, "04_conflict_reconciliation.png"), full_page=False)

    print("[5/5] Capturing 05_central_knowledge_explorer.png...")
    # Switch to Central Knowledge Explorer tab
    page.locator("button:has-text('Central Knowledge Explorer')").first.click()
    time.sleep(1)
    page.screenshot(path=os.path.join(output_dir, "05_central_knowledge_explorer.png"), full_page=False)

    # Reconnect LAN mode before closing
    reconnect_btn = page.locator("button:has-text('Reconnect LAN')")
    if reconnect_btn.count() > 0:
        reconnect_btn.first.click()
        time.sleep(0.5)

    browser.close()
    print("All screenshots successfully captured into ./docs/screenshots/")
