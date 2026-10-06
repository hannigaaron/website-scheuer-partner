#!/usr/bin/env python3
"""Exportiert jede SVG-Fassung als PNG mit transparentem Hintergrund (2000 px breit)."""
import pathlib
from playwright.sync_api import sync_playwright
HERE = pathlib.Path(__file__).resolve().parent
SVG = HERE / "logos/svg"; PNG = HERE / "logos/png"; PNG.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 2000, 'height': 1400})
    for f in sorted(SVG.glob("*.svg")):
        svg = f.read_text(encoding="utf-8").replace("<svg ", '<svg style="width:2000px;height:auto" ', 1)
        pg.set_content('<body style="margin:0;background:transparent"><div id="x" style="width:2000px;line-height:0">' + svg + '</div></body>')
        pg.locator('#x').screenshot(path=str(PNG / (f.stem + ".png")), omit_background=True)
    b.close()
print(len(list(PNG.glob("*.png"))), "PNG")
