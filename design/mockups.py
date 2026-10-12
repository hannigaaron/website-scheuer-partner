#!/usr/bin/env python3
"""Mockups: Briefbogen, Visitenkarte, Website-Kopf für die Logos 11, 13 und 19.
Ausgabe: design/mockups/ (PDF + PNG je Logo und Gesamt-PDF)."""
import base64, pathlib, re
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "mockups"; OUT.mkdir(exist_ok=True)
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
CHOICES = [("11", "11-siegel-serife", "Siegel mit Serifen"),
           ("13", "13-siegel-bogen", "Siegel mit Bogen"),
           ("19", "19-dreifach-bogen", "Dreifachbogen, nur Kontur")]

def b64(p): return base64.b64encode(pathlib.Path(p).read_bytes()).decode()

def tight(svg):
    m = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"', svg)
    x, y, w, h = map(float, m.groups())
    svg = svg.replace(m.group(0), f'viewBox="{x+34:.1f} {y+34:.1f} {w-68:.1f} {h-68:.1f}"')
    svg = re.sub(r' width="\d+" height="\d+"', '', svg, 1)
    return svg, (w - 68) / (h - 68)

def logo(key, variant="farbe", css="height:100%"):
    s, ratio = tight((HERE / "logos2/svg" / f"{key}-{variant}.svg").read_text(encoding="utf-8"))
    return s.replace("<svg ", f'<svg style="{css};width:auto;display:block" ', 1), ratio

FONTS = ROOT / "fonts"
CSS = f"""
@font-face{{font-family:'Cormorant Garamond';font-weight:400 600;src:url(data:font/woff2;base64,{b64(FONTS/'cormorant-garamond-normal-latin.woff2')})}}
@font-face{{font-family:'Inter';font-weight:100 900;src:url(data:font/woff2;base64,{b64(FONTS/'inter-normal-latin.woff2')})}}
@page{{size:297mm 210mm;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Inter,sans-serif;color:#262626;background:#fff}}
.page{{width:297mm;height:210mm;background:#ecece8;position:relative;overflow:hidden;page-break-after:always}}
.ptitle{{position:absolute;left:12mm;top:9mm;font-family:'Cormorant Garamond',serif;font-weight:500;font-size:26px;color:#262626}}
.ptitle small{{font-family:Inter;font-size:11px;color:#5b5b5b;letter-spacing:.14em;text-transform:uppercase;margin-left:12px}}
.lbl{{position:absolute;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#5b5b5b}}
.shadow{{box-shadow:0 2px 4px rgba(0,0,0,.08),0 12px 30px rgba(0,0,0,.14)}}
/* Briefbogen 210x297mm bei 96dpi = 794x1123 */
.sheet{{width:794px;height:1123px;background:#fff;position:absolute;transform-origin:0 0}}
.sheet .lg{{position:absolute;left:76px;top:62px;height:78px}}
.sheet .addr{{position:absolute;left:76px;top:210px;width:320px;font-size:12.5px;line-height:1.45}}
.sheet .addr small{{display:block;font-size:8.5px;color:#5b5b5b;border-bottom:.6px solid #5b5b5b;padding-bottom:3px;margin-bottom:9px;width:300px}}
.sheet .info{{position:absolute;left:520px;top:210px;width:200px;font-size:10.5px;line-height:1.6;color:#5b5b5b}}
.sheet .info b{{color:#262626;font-weight:500}}
.sheet .body{{position:absolute;left:76px;top:440px;width:640px;font-size:12.5px;line-height:1.55}}
.sheet .body h4{{font-weight:600;font-size:12.5px;margin-bottom:22px}}
.sheet .body p{{margin-bottom:12px}}
.sheet .ft{{position:absolute;left:76px;right:74px;bottom:46px;border-top:1.5px solid #16a355;padding-top:12px;display:grid;grid-template-columns:1.1fr 1fr 1.2fr;gap:18px;font-size:8.6px;line-height:1.5;color:#5b5b5b}}
.sheet .ft b{{color:#262626;font-weight:500}}
.fold{{position:absolute;left:0;width:14px;border-top:.8px solid #bbb}}
/* Visitenkarte 85x55mm = 321x208 */
.card{{width:321px;height:208px;background:#fff;position:absolute;transform-origin:0 0;overflow:hidden}}
.card.front .lg{{position:absolute;left:34px;right:34px;top:34px;bottom:34px;display:flex;align-items:center;justify-content:center}}
.card.front .lg svg{{width:100%;height:auto;max-height:100%}}
.card.back{{padding:26px 28px}}
.card.back .nm{{font-family:'Cormorant Garamond',serif;font-weight:500;font-size:21px;line-height:1}}
.card.back .rl{{font-size:8.5px;color:#0d7a3f;letter-spacing:.1em;text-transform:uppercase;margin-top:6px;font-weight:500}}
.card.back .ct{{position:absolute;left:28px;bottom:26px;font-size:8.4px;line-height:1.6;color:#5b5b5b}}
.card.back .ct b{{color:#262626;font-weight:500}}
.card.back .mk{{position:absolute;right:26px;top:24px;height:30px}}
.card.back::after{{content:"";position:absolute;left:0;right:0;bottom:0;height:5px;background:#16a355}}
/* Website */
.web{{position:absolute;background:#fff;overflow:hidden;transform-origin:0 0}}
.web .nav{{display:flex;align-items:center;justify-content:space-between;padding:0 40px;height:92px;border-bottom:1px solid #e4e4e0}}
.web .nav ul{{display:flex;gap:30px;list-style:none;font-size:14px;color:#262626}}
.web .nav .btn{{background:#16a355;color:#fff;font-size:13px;font-weight:500;padding:13px 22px}}
.web .hero{{display:grid;grid-template-columns:1fr 1.15fr;height:430px}}
.web .hero .tx{{padding:70px 40px 0 40px}}
.web .hero .ey{{font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:#0d7a3f;font-weight:500}}
.web .hero h1{{font-family:'Cormorant Garamond',serif;font-weight:500;font-size:68px;line-height:1;margin-top:20px}}
.web .hero h1 em{{font-style:normal;color:#16a355}}
.web .hero img{{width:100%;height:100%;object-fit:cover;display:block}}
.web.m .nav{{height:72px;padding:0 18px}}
.web.m .burger{{width:26px;height:18px;border-top:2px solid #262626;border-bottom:2px solid #262626;position:relative}}
.web.m .burger::after{{content:"";position:absolute;left:0;right:0;top:6px;border-top:2px solid #262626}}
.web.m .hero{{display:block;height:auto}}
.web.m .hero .tx{{padding:30px 18px 24px}}
.web.m .hero h1{{font-size:46px}}
.web.m .hero img{{height:230px}}
"""

def sheet(key):
    lg, r = logo(key, css="height:100%")
    return f"""<div class="sheet shadow" style="left:12mm;top:24mm;transform:scale(.6)">
 <div class="lg" style="width:{78*r:.0f}px">{lg}</div>
 <div class="addr"><small>Scheuer &amp; Partner mbB · In den Freßäckern 10 · 74321 Bietigheim-Bissingen</small>Frau<br>Erika Mustermann<br>Musterstraße 1<br>12345 Musterstadt</div>
 <div class="info"><b>Ihr Ansprechpartner</b><br>Sandra Häusser<br>Telefon 07142 7000-0<br>s.haeusser@scheuer-partner.de<br><br><b>Datum</b><br>12.10.2026</div>
 <div class="body"><h4>Ihre Einkommensteuererklärung</h4>
  <p>Sehr geehrte Frau Mustermann,</p>
  <p>dies ist ein Mustertext, der den Schriftsatz auf dem Briefbogen zeigt. Er ist ohne Inhalt und dient nur der Ansicht von Schrift, Abständen und Fußzeile.</p>
  <p>Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.</p>
  <p>At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est.</p>
  <p style="margin-top:26px">Mit freundlichen Grüßen<br><br><br>Sandra Häusser<br>Steuerberaterin</p></div>
 <div class="fold" style="top:421px"></div><div class="fold" style="top:561px;width:20px"></div><div class="fold" style="top:842px"></div>
 <div class="ft"><div><b>Scheuer &amp; Partner mbB</b><br>Steuerberatungsgesellschaft<br>In den Freßäckern 10<br>74321 Bietigheim-Bissingen</div>
  <div>Telefon 07142 7000-0<br>Telefax 07142 7000-99<br>mail@scheuer-partner.de<br>www.scheuer-partner.de</div>
  <div>Partnerschaftsregister Amtsgericht Stuttgart PR 300017<br>USt-IdNr. DE240236851<br>Vertretungsberechtigt: Sandra Häusser, Jasmin Titscher</div></div>
</div>
<div class="lbl" style="left:12mm;top:17mm">Briefbogen DIN A4</div>"""

def cards(key):
    lf, r = logo(key, css="width:100%")
    mark, _ = logo(key, css="height:100%")
    return f"""<div class="lbl" style="left:150mm;top:17mm">Visitenkarte 85 × 55 mm, Vorder- und Rückseite</div>
<div class="card front shadow" style="left:150mm;top:24mm;transform:scale(.78)"><div class="lg">{lf}</div></div>
<div class="card back shadow" style="left:220mm;top:24mm;transform:scale(.78)">
 <div class="nm">Sandra Häusser</div><div class="rl">Steuerberaterin</div>
 <div class="ct"><b>Scheuer &amp; Partner mbB</b><br>In den Freßäckern 10, 74321 Bietigheim-Bissingen<br>Telefon 07142 7000-0<br>s.haeusser@scheuer-partner.de<br>www.scheuer-partner.de</div></div>"""

def web(key):
    ld, r = logo(key, css="height:100%")
    lm, rm = logo(key, css="height:100%")
    nav = '<li>Über uns</li><li>Team</li><li>Steuerberatung</li><li>Service</li><li>Kontakt</li>'
    return f"""<div class="lbl" style="left:182mm;top:{24+55*2*.98+14:.0f}mm">Website-Kopf, Desktop und Handy</div>
<div class="web shadow" style="left:182mm;top:{24+55*2*.98+21:.0f}mm;width:1440px;height:522px;transform:scale(.0745)"></div>"""

def build_page(key, name, title):
    num = key[:2]
    ld, r = logo(key)
    nav = '<li>Über uns</li><li>Team</li><li>Steuerberatung</li><li>Service</li><li>Kontakt</li>'
    hero = (ROOT / "img/hero.jpg")
    img = "data:image/jpeg;base64," + b64(hero)
    desk = f"""<div class="web shadow" style="left:182mm;top:132mm;width:1440px;height:522px;transform:scale(.0745)">
<div class="nav"><div style="height:60px">{logo(key)[0]}</div><ul>{nav}</ul><span class="btn">Online-Portal</span></div>
<div class="hero"><div class="tx"><div class="ey">Steuerberatungsgesellschaft</div><h1>Scheuer<br><em>&amp; Partner</em></h1></div><img src="{img}"></div></div>"""
    # Maßstab: 1440px -> 70mm  => scale = 70mm/1440px
    desk = desk.replace("transform:scale(.0745)", "transform:scale(.2487)")  # 70mm = 264.6px; /1440 = .1837 (siehe unten)
    return num, desk

def page(key, name, title):
    num = key[:2]
    nav = '<li>Über uns</li><li>Team</li><li>Steuerberatung</li><li>Service</li><li>Kontakt</li>'
    img = "data:image/jpeg;base64," + b64(ROOT / "img/hero.jpg")
    # Desktop: 1440 px -> 100 mm Breite = 378 px => scale .2625 ; Handy: 390 px -> 30 mm = 113 px => .29
    desk = f"""<div class="lbl" style="left:150mm;top:74mm">Website-Kopf: Desktop</div>
<div class="web shadow" style="left:150mm;top:81mm;width:1440px;height:522px;transform:scale(.354)">
<div class="nav"><div style="height:60px">{logo(key)[0]}</div><ul>{nav}</ul><span class="btn">Online-Portal</span></div>
<div class="hero"><div class="tx"><div class="ey">Steuerberatungsgesellschaft</div><h1>Scheuer<br><em>&amp; Partner</em></h1></div><img src="{img}"></div></div>
<div class="lbl" style="left:150mm;top:137mm">Website-Kopf: Handy</div>
<div class="web m shadow" style="left:150mm;top:144mm;width:390px;height:520px;transform:scale(.354)">
<div class="nav"><div style="height:44px">{logo(key)[0]}</div><div class="burger"></div></div>
<div class="hero"><div class="tx"><div class="ey">Steuerberatung</div><h1>Scheuer<br><em>&amp; Partner</em></h1></div><img src="{img}"></div></div>"""
    return f"""<div class="page"><div class="ptitle">Logo {num}<small>{title}</small></div>{sheet(key)}{cards(key)}{desk}</div>"""

def main():
    pages = [page(n, n, t) for k, n, t in CHOICES]
    html = f"<!doctype html><meta charset=utf-8><style>{CSS}</style>" + "".join(pages)
    (OUT / "mockups.html").write_text(html, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
        pg = b.new_page(viewport={'width': 1123, 'height': 794}, device_scale_factor=2)
        pg.goto("file://" + str(OUT / "mockups.html"))
        pg.wait_for_timeout(600)
        pg.pdf(path=str(OUT / "Mockups-Scheuer-Partner.pdf"), width="297mm", height="210mm", print_background=True)
        for i, (k, n, t) in enumerate(CHOICES):
            pg.locator(".page").nth(i).screenshot(path=str(OUT / f"mockup-{k}.png"))
        b.close()
    print("fertig")
main()
