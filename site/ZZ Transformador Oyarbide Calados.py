import os
import re
import requests
from playwright.sync_api import sync_playwright

SVG_SOURCE_URL = "https://api.shn.gob.ar/imagenes-modelo/curvas_altura-total/Alturatotal_Oyarvide.svg"
OUTPUT_BASENAME = "Punta_Indio"

OLD_TITLE_CONTENT = "Altura del nivel del agua por efecto meteorológico y de marea astronómica"
NEW_TITLE_CONTENT = "RIVER PLATE Wind Corrected Tides with Sailing Drafts | (Numerical Tide Forecast)"

DRAFT_BY_TIDE = {
    -0.1: 9.70, 0.0: 9.80, 0.1: 9.90, 0.2: 10.00, 0.3: 10.10,
    0.4: 10.20, 0.5: 10.30, 0.6: 10.37, 0.7: 10.41, 0.8: 10.45,
    0.9: 10.49, 1.0: 10.53, 1.1: 10.57, 1.2: 10.61, 1.3: 10.65,
    1.4: 10.72, 1.5: 10.81, 1.6: 10.90, 1.7: 10.99, 1.8: 11.08,
    1.9: 11.17, 2.0: 11.27, 2.1: 11.36, 2.2: 11.45
}
TOLERANCE = 0.051


def parse_tick(raw: str):
    raw = raw.strip().replace(",", ".")
    if raw.endswith("m"):
        raw = raw[:-1]
    try:
        return float(raw)
    except ValueError:
        return None


def snap_to_key(v: float):
    best, err = None, 999.0
    for k in DRAFT_BY_TIDE:
        e = abs(v - k)
        if e < err:
            best, err = k, e
    return best if err <= TOLERANCE else None


def modify_svg(svg: str) -> str:
    text_re = re.compile(
        r'(<text[^>]*x=["\']-5["\'][^>]*y=["\']([\d.]+)[^>]*>)(.*?)(</text>)'
    )

    out = svg
    for prefix, y, raw, _suffix in text_re.findall(svg):
        tide = parse_tick(raw)
        if tide is None:
            continue
        key = snap_to_key(tide)
        if key is None:
            continue
        draft = DRAFT_BY_TIDE[key]

        repl = (
            f'<text x="115" y="{y}" text-anchor="end" '
            f'font-size="25" fill="blue">'
            f'Tide {key:.1f} = Draft {draft:.2f} m</text>'
        )

        out = out.replace(prefix + raw + "</text>", repl)

    out = out.replace(OLD_TITLE_CONTENT, NEW_TITLE_CONTENT)
    out = out.replace("TORRE OYARVIDE", "")
    out = out.replace("(Las horas están referidas a la HOA)", "")

    return out


def main():
    # Repo root is parent of this file because your script is in /site
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(here)

    out_dir = os.path.join(repo_root, "docs")
    os.makedirs(out_dir, exist_ok=True)

    svg_path = os.path.join(out_dir, OUTPUT_BASENAME + ".svg")
    png_path = os.path.join(out_dir, OUTPUT_BASENAME + ".png")
    html_path = os.path.join(out_dir, "index.html")

    # Fetch source SVG
    r = requests.get(SVG_SOURCE_URL, timeout=30)
    r.raise_for_status()

    # Transform SVG
    svg = modify_svg(r.text)

    # Save SVG
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)

    # Build HTML (used for both Pages and Playwright screenshot)
    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{OUTPUT_BASENAME}</title>
  <style>
    body {{ margin: 0; background: white; }}
  </style>
</head>
<body>
{svg}
</body>
</html>
"""

    # Save HTML for GitHub Pages
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Render PNG via Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 1000})
        page.set_content(html)
        page.screenshot(path=png_path, full_page=True)
        browser.close()

    print("CREATED:")
    print(svg_path)
    print(png_path)
    print(html_path)


if __name__ == "__main__":
    main()
