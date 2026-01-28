import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

WINDGURU_URL = "https://www.windguru.cz/968903"  # keep yours

def safe_click(page, selectors, timeout=6000):
    """Try a list of selectors; click the first that matches."""
    for sel in selectors:
        try:
            page.locator(sel).first.click(timeout=timeout)
            return True
        except Exception:
            pass
    return False

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(here)

    out_dir = os.path.join(repo_root, "docs", "assets")
    os.makedirs(out_dir, exist_ok=True)
    out_png = os.path.join(out_dir, "WINDGURU.png")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1600, "height": 420})
        page.goto(WINDGURU_URL, wait_until="domcontentloaded")

        # Give page time to render
        page.wait_for_timeout(4000)

        # Try dismiss cookie/consent banners if present (best effort)
        safe_click(page, [
            "button:has-text('Accept')",
            "button:has-text('I agree')",
            "text=I agree",
            "text=Accept all",
            "button:has-text('AGREE')",
        ], timeout=2500)

        # Click the top tab "Compare" (your screenshot)
        clicked = safe_click(page, [
            "text=Compare",
            "a:has-text('Compare')",
            "button:has-text('Compare')",
            "[id*='compare']",
        ], timeout=6000)

        # If click didn’t work, still proceed (some pages load already on compare-like view)
        page.wait_for_timeout(3000)

        # BASELINE screenshot of the viewport (cropping/element-shot comes next step)
        page.screenshot(path=out_png, full_page=False)

        browser.close()

    print("CREATED:", out_png)

if __name__ == "__main__":
    main()
