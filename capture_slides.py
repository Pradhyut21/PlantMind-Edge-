import os
import time
from playwright.sync_api import sync_playwright

def capture_slides():
    print("Capturing 1080p slide frames from HTML PPT Presenter...")
    frames_dir = os.path.abspath("brag-output/slides")
    os.makedirs(frames_dir, exist_ok=True)

    html_path = os.path.abspath("presentation/index.html").replace("\\", "/")
    url = f"file:///{html_path}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(url)
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        for i in range(1, 9):
            print(f"  Rendering Slide {i}...")
            # Use the PPT API to navigate to slide
            page.evaluate(f"window.__PPT__.goTo({i})")
            time.sleep(0.8) # wait for smooth slide transition to settle

            out_path = os.path.join(frames_dir, f"slide_{i}.png")
            page.screenshot(path=out_path, full_page=False)
            print(f"    Saved {out_path} ({os.path.getsize(out_path)} bytes)")

        browser.close()
    print("All 8 slides captured at 1920x1080!")

if __name__ == "__main__":
    capture_slides()
