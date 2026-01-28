import os
from playwright.sync_api import sync_playwright

WINDGURU_URL = "https://www.windguru.cz/968903"

# Map: row label -> option to click inside its dropdown menu
ROW_CHOICES = {
    "Wind speed (knots)": "GFS 13 km",
    "Wind gusts (knots)": "GFS 13 km",
    "Wind direction": "GFS 13 km",
    # add more if you want:
    # "Temperature (°C)": "GFS 13 km",
}

def click_if_exists(page, selector, timeout=2500):
    try:
        page.locator(selector).first.click(timeout=timeout)
        return True
    except Exception:
        return False

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(here)
    out_dir = os.path.join(repo_root, "docs", "assets")
    os.makedirs(out_dir, exist_ok=True)
    out_png = os.path.join(out_dir, "WINDGURU.png")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1700, "height": 520})
        page.goto(WINDGURU_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        # Consent (best effort)
        click_if_exists(page, "button:has-text('Accept')")
        click_if_exists(page, "button:has-text('I agree')")
        click_if_exists(page, "text=Accept all")

        # Click Compare
        page.locator("text=Compare").first.click(timeout=6000)
        page.wait_for_timeout(2500)

        # ---- Pick model per row via the small caret dropdown ----
        for row_label, option_text in ROW_CHOICES.items():
            # 1) find the row by its label text
            row = page.locator(f"text={row_label}").first

            # 2) click the caret within the same row line (usually a small ▼ on the right)
            # We go up to a parent container and then look for a clickable caret-like element.
            container = row.locator("xpath=ancestor::*[self::tr or self::div][1]")

            # Try a few patterns for the caret
            clicked = False
            for caret_sel in [
                "css=span:has-text('▼')",
                "css=span.wg-select",
                "css=.caret",
                "css=.arrow",
                "css=[class*='arrow']",
                "css=[class*='caret']",
                "css=svg",  # sometimes the caret is an svg icon
            ]:
                try:
                    container.locator(caret_sel).first.click(timeout=1500)
                    clicked = True
                    break
                except Exception:
                    pass

            if not clicked:
                # fallback: click near the label (often opens the menu)
                try:
                    row.click(timeout=1500)
                except Exception:
                    pass

            page.wait_for_timeout(600)

            # 3) click the option inside the opened menu
            # The menu often appears as a floating panel; we just click the visible text.
            try:
                page.locator(f"text={option_text}").first.click(timeout=2500)
            except Exception:
                # if option not found, close menu to avoid overlay
                page.keyboard.press("Escape")

            page.wait_for_timeout(600)
            page.keyboard.press("Escape")  # close any remaining menu

        page.wait_for_timeout(1500)

        # ---- Crop: screenshot only the forecast grid area ----
        # We target a stable container around the colored grid + arrows.
        # (These selectors are tried in order.)
        candidates = [
            "css=div:has(text('Wind speed (knots)'))",
            "css=div:has(text('Wind gusts (knots)'))",
            "css=div:has(text('WG'))",
            "css=body",
        ]

        # Best effort: choose the smallest container that still holds the table.
        shot_done = False
        for sel in candidates:
            loc = page.locator(sel).first
            try:
                if loc.is_visible():
                    # If body is selected, it will be too big, but it’s a safe fallback.
                    loc.screenshot(path=out_png)
                    shot_done = True
                    break
            except Exception:
                pass

        if not shot_done:
            page.screenshot(path=out_png, full_page=False)

        browser.close()

    print("CREATED:", out_png)

if __name__ == "__main__":
    main()
