#!/usr/bin/env python3
"""Übersichtsblätter der Logo-Entwürfe: je Logo auf Weiß und auf Schwarz.
Erzeugt PNG und PDF in design/logos/. Aufruf nach make_logos.py."""
import html, pathlib, re
from playwright.sync_api import sync_playwright
from make_logos import LOGOS, OUT, HERE

CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
F = (HERE / "fonts").as_uri()

def svg_of(num, key, variant):
    s = (OUT / "svg" / f"{num}-{key}-{variant}.svg").read_text(encoding="utf-8")
    return re.sub(r'<svg ', '<svg role="img" ', s, 1)

def row(num, key, name, desc):
    return f'''<div class="row">
  <div class="lab"><span class="n">{num}</span><h2>{html.escape(name)}</h2><p>{html.escape(desc)}</p></div>
  <div class="tile light">{svg_of(num, key, "farbe")}</div>
  <div class="tile dark">{svg_of(num, key, "negativ")}</div>
</div>'''

def page(items, nr, total):
    rows = "".join(row(*i[:3], i[4]) for i in items)
    return f'''<section class="page"><header><div><h1>Scheuer &amp; Partner</h1><p>Logo-Entwürfe, erste Runde</p></div><span>Seite {nr} von {total}</span></header>{rows}</section>'''

CSS = f'''
@font-face{{font-family:"CG";src:url({F}/CormorantGaramond-normal.woff2);font-weight:300 700}}
@font-face{{font-family:"IN";src:url({F}/Inter-normal.woff2);font-weight:400 700}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#fff;font-family:"IN",sans-serif;color:#262626}}
.page{{width:1800px;height:2060px;padding:56px 64px 40px;display:flex;flex-direction:column;page-break-after:always;background:#fff}}
header{{display:flex;justify-content:space-between;align-items:flex-end;padding-bottom:22px;border-bottom:2px solid #16A355;margin-bottom:26px}}
header h1{{font-family:"CG",serif;font-weight:600;font-size:54px;line-height:1}}
header p{{font-size:18px;color:#5b5b5b;margin-top:8px}}
header span{{font-size:16px;color:#838383;letter-spacing:.08em}}
.row{{display:grid;grid-template-columns:340px 1fr 1fr;gap:20px;height:352px;margin-bottom:20px}}
.lab{{padding:6px 14px 0 0}}
.n{{font-family:"CG",serif;font-style:italic;font-size:44px;color:#16A355;line-height:1}}
.lab h2{{font-family:"CG",serif;font-weight:600;font-size:36px;margin:8px 0 10px}}
.lab p{{font-size:16px;line-height:1.5;color:#5b5b5b}}
.tile{{display:grid;place-items:center;border:1px solid rgba(0,0,0,.12);overflow:hidden}}
.tile.dark{{background:#000;border-color:#000}}
.tile svg{{width:auto;height:auto;max-width:84%;max-height:240px}}
'''

def main():
    pages = [LOGOS[:5], LOGOS[5:]]
    body = "".join(page(p, i + 1, len(pages)) for i, p in enumerate(pages))
    html_doc = f'<!doctype html><meta charset="utf-8"><style>{CSS}</style>{body}'
    (OUT / "uebersicht.html").write_text(html_doc, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
        pg = b.new_page(viewport={'width': 1800, 'height': 2060})
        pg.goto((OUT / "uebersicht.html").as_uri()); pg.wait_for_timeout(600)
        for i, el in enumerate(pg.query_selector_all('.page')):
            el.screenshot(path=str(OUT / f"uebersicht-{i + 1}.png"))
        pg.pdf(path=str(OUT / "uebersicht.pdf"), width='1800px', height='2060px', print_background=True)
        b.close()
    print("Übersichten fertig")

if __name__ == "__main__":
    main()
