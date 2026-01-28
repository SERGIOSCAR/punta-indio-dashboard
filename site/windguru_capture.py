import os
from playwright.sync_api import sync_playwright

WINDGURU_URL = "https://www.windguru.cz/968903"

# What you want each row to use:
ROW_CHOICES = {
    "Wind speed (knots)": "GFS 13 km",
    "Wind gusts (knots)": "GFS 13 km",
    "Wind direction": "GFS 13 km",
}

def click_if_exists(page, selector, timeout=2500):
    try:
        page.locator(selector).first.click(timeout=timeout)
        return True
    except Exception:
        return False

def click_row_dropdown_and_pick(page, row_label: str, option_text: str):
    """
    Finds the row by label text, clicks its dropdown caret, then clicks the desired option.
    """
    # Anchor on the row label cell
    row_label_loc = page.locator(f"text={row_label}").first

    # Go up to the nearest row container (table row)
    row = row_label_loc.locator("xpath=ancestor::tr[1]")

    # The dropdown caret is typically in the same row, at the far right of the label cell.
    # We try a few likely clickable targets inside that row.
    caret_selectors = [
        "css=td >> css=span:has-text('▼')",
        "css=td >> css=span:has-text('▾')",
        "css=td >> css=[class*='caret']",
        "css=td >> css=[class*='arrow']",
        "css=td >> css=svg",
    ]

    clicked = False
    for sel in caret_selectors:
        try:
            row.locator(sel).first.click(timeout=1200)
            clicked = True
            break
        except Exception:
            pass

    # Fallback: click near the label (often opens the menu)
    if not clicked:
        try:
            row_label_loc.click(timeout=1200)
        except Exception:
            pass

    page.wait_for_timeout(500)

    # Click option inside opened menu
    # The menu is floating; we pick by visible text.
    page.locator(f"text={option_text}").first.click(timeout=3000)

    page.wait_for_timeout(400)
    page.keyboard.press("Escape")  # close menu if it stays open

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
        page.wait_for_timeout(3500)

        # Consent (best effort)
        click_if_exists(page, "button:has-text('Accept')")
        click_if_exists(page, "button:has-text('I agree')")
        click_if_exists(page, "text=Accept all")

        # Click Compare tab
        page.locator("text=Compare").first.click(timeout=6000)
        page.wait_for_timeout(2500)

        # Ensure the English compare table is present
        page.locator("text=Wind speed (knots)").first.wait_for(timeout=8000)

        # Apply row dropdown picks
        for row_label, opt in ROW_CHOICES.items():
            click_row_dropdown_and_pick(page, row_label, opt)

        page.wait_for_timeout(1200)

        # ---- Crop to the compare table only ----
        # Target the table that contains "Wind speed (knots)" and screenshot that table element.
        table = page.locator("xpath=//table[.//text()[contains(., 'Wind speed (knots)')]]").first
        if table.is_visible():
            table.screenshot(path=out_png)
        else:
            # fallback: viewport screenshot
            page.screenshot(path=out_png, full_page=False)

        browser.close()

    print("CREATED:", out_png)

if __name__ == "__main__":
    main()
