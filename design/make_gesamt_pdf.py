#!/usr/bin/env python3
"""Eine PDF mit allen Logo-Entwürfen (01 bis 20): erste Seite alle auf einen Blick,
danach je fünf Logos pro Seite auf Weiß und auf Schwarz. Vektoren bleiben Vektoren.
Aufruf im Ordner design/:  python3 make_gesamt_pdf.py"""
import html
import pathlib
from playwright.sync_api import sync_playwright

import make_sheets
from make_logos import LOGOS, OUT as OUT1
from runde2 import LOGOS2, OUT as OUT2

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / "Logo-Gesamtuebersicht-Scheuer-Partner.pdf"
ALL = [(l, OUT1 / "svg") for l in LOGOS] + [(l, OUT2 / "svg") for l in LOGOS2]
TOTAL = 5

EXTRA = '''
@page{size:1800px 2060px;margin:0}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:22px 20px;flex:1}
.cell{display:flex;flex-direction:column;gap:9px}
.cell .tile{height:290px}
.cap{display:flex;align-items:baseline;gap:12px;font-size:17px;color:#262626}
.cap b{font-family:"CG",serif;font-style:italic;font-weight:500;font-size:28px;color:#16A355}
'''


def cell(item, svgdir):
    num, key, name = item[0], item[1], item[2]
    return (f'<div class="cell"><div class="tile light">{make_sheets.svg_of(num, key, "farbe", svgdir)}</div>'
            f'<div class="cap"><b>{num}</b>{html.escape(name)}</div></div>')


def main():
    cells = "".join(cell(i, d) for i, d in ALL)
    first = (f'<section class="page"><header><div><h1>Scheuer &amp; Partner</h1>'
             f'<p>Alle Logo-Entwürfe auf einen Blick, 01 bis 20</p></div><span>Seite 1 von {TOTAL}</span></header>'
             f'<div class="grid">{cells}</div></section>')
    pages = [first]
    n = 2
    for chunk in (LOGOS[:5], LOGOS[5:], LOGOS2[:5], LOGOS2[5:]):
        svgdir = OUT1 / "svg" if chunk[0] in LOGOS else OUT2 / "svg"
        runde = "erste Runde" if chunk[0] in LOGOS else "zweite Runde"
        pages.append(make_sheets.page(chunk, n, TOTAL, svgdir, f"Logo-Entwürfe, {runde}, je auf Weiß und auf Schwarz"))
        n += 1
    doc = f'<!doctype html><meta charset="utf-8"><style>{make_sheets.CSS}{EXTRA}</style>{"".join(pages)}'
    tmp = HERE / "gesamt.html"
    tmp.write_text(doc, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=make_sheets.CHROME, args=['--no-sandbox'])
        pg = b.new_page(viewport={'width': 1800, 'height': 2060})
        pg.goto(tmp.as_uri()); pg.wait_for_timeout(700)
        pg.pdf(path=str(TARGET), width='1800px', height='2060px', print_background=True)
        pg.query_selector_all('.page')[0].screenshot(path=str(HERE / "gesamt-seite1.png"))
        b.close()
    tmp.unlink()
    print("PDF fertig:", TARGET.name, TARGET.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
