import os
from playwright.sync_api import sync_playwright

WINDGURU_URL = "https://www.windguru.cz/968903"

def safe_click(page, selectors, timeout=6000):
    for sel in selectors:
        try:
            page.locator(sel).first.click(timeout=timeout)
            return True
        except Exception:
            pass
    return False

def safe_select(page, selectors, value=None, label=None, timeout=6000):
    """
    Try selecting an option from a <select>.
    Provide either value="..." or label="..." (visible text).
    """
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if value is not None:
                loc.select_option(value=value, timeout=timeout)
            else:
                loc.select_option(label=label, timeout=timeout)
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
        page = browser.new_page(viewport={"width": 1600, "height": 500})
        page.goto(WINDGURU_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        # Cookie/consent (best effort)
        safe_click(page, [
            "button:has-text('Accept')",
            "button:has-text('I agree')",
            "text=I agree",
            "text=Accept all",
        ], timeout=2500)

        # Click Compare
        safe_click(page, ["text=Compare", "a:has-text('Compare')", "button:has-text('Compare')"], timeout=6000)
        page.wait_for_timeout(2000)

        # ---- 3 dropdowns (generic approach) ----
        # Windguru often has multiple <select> controls on the compare bar.
        # We select by "label" (visible option text). Adjust the labels to match your exact choices.

        # Dropdown #1 (model / source) - EXAMPLE
        safe_select(page,
            selectors=[
                "select >> nth=0",
            ],
            label="GFS 13 km"
        )

        # Dropdown #2 (another model/source) - EXAMPLE
        safe_select(page,
            selectors=[
                "select >> nth=1",
            ],
            label="ICON 13 km"
        )

        # Dropdown #3 (display mode / table type) - EXAMPLE
        safe_select(page,
            selectors=[
                "select >> nth=2",
            ],
            label="Wind"
        )

        page.wait_for_timeout(2500)

        # ---- Cropped element screenshot (forecast grid) ----
        # Try common containers; we take the first visible one.
        grid_candidates = [
            "table",                 # sometimes the forecast is a table
            "div.wgfc",              # Windguru often uses wgfc-like classes
            "div#forecast",          # common id pattern
            "div:has-text('Updated')",  # fallback anchor near the grid
        ]

        shot_done = False
        for sel in grid_candidates:
            loc = page.locator(sel).first
            try:
                if loc.is_visible():
                    # Element screenshot = clean crop
                    loc.screenshot(path=out_png)
                    shot_done = True
                    break
            except Exception:
                pass

        # Fallback: if element not found, screenshot viewport
        if not shot_done:
            page.screenshot(path=out_png, full_page=False)

        browser.close()

    print("CREATED:", out_png)

if __name__ == "__main__":
    main()
