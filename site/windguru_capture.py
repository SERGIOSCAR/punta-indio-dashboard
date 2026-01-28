import os
from playwright.sync_api import sync_playwright

# Paste the exact Windguru page URL you use for "Zona Comun"
WINDGURU_URL = "https://www.windguru.cz/968903"

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(here)

    out_dir = os.path.join(repo_root, "docs", "assets")
    os.makedirs(out_dir, exist_ok=True)

    out_png = os.path.join(out_dir, "WINDGURU.png")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        page.goto(WINDGURU_URL, wait_until="domcontentloaded")

        # allow dynamic table to render
        page.wait_for_timeout(9000)

        # baseline screenshot (we'll crop later)
        page.screenshot(path=out_png, full_page=True)

        browser.close()

    print("CREATED:", out_png)

if __name__ == "__main__":
    main()
