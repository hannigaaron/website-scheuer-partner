#!/usr/bin/env python3
"""Erzeugt alle HTML-Seiten aus gemeinsamen Bausteinen.

Aufruf im Repo-Ordner:  python3 tools/build.py
Die Seiten werden im Hauptverzeichnis abgelegt und mit committet. Auf dem
Server läuft kein Build, die Seite bleibt rein statisch.
Alle Texte stammen im Wortlaut von der bisherigen Kanzleiseite.
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINKS = json.loads((ROOT / "tools/source/links.json").read_text(encoding="utf-8"))

NAME = "Scheuer & Partner mbB Steuerberatungsgesellschaft"
PORTAL = "https://scheuer-partner.portal-bereich.de"
MAPS = "https://www.google.com/maps/search/?api=1&query=In+den+Fre%C3%9F%C3%A4ckern+10%2C+74321+Bietigheim-Bissingen"
OSM = "https://www.openstreetmap.org/search?query=In%20den%20Fre%C3%9F%C3%A4ckern%2010%2C%2074321%20Bietigheim-Bissingen"
OLD = "https://www.scheuer-partner.de"
NEWS_OKT = OLD + "/de/news/steuernews_f%C3%BCr_mandanten/oktober_2026/elektronische_fuehrung_ergaenzender_entgeltunterlagen/"
NEWS_ARZT = OLD + "/de/news/steuernews_f%C3%BCr_%C3%A4rzte/herbst_2026/bmf_schreiben_zur_umsatzsteuerbefreiung_fuer_schoenheitsoperationen/"
MAIL = "mail@scheuer-partner.de"

e = html.escape


# ---------------------------------------------------------------------------
# Hilfen
# ---------------------------------------------------------------------------
def link(page, needle, nth=0):
    """Passende Adresse und Beschreibung aus den gesammelten Links der alten Seite."""
    hits = [(h, t) for h, t in LINKS[page] if needle.lower() in h.lower()]
    if not hits:
        raise SystemExit(f"Link nicht gefunden: {page} / {needle}")
    return hits[nth]


def card(page, title, needle, nth=0, meta=None):
    href, text = link(page, needle, nth)
    desc = text[len(title):].strip() if text.startswith(title) else ""
    desc = re.sub(r"^\(.*?\)\s*", "", desc)
    m = meta
    if m is None:
        mm = re.search(r"\((<?\s*[\d.,]+\s*(?:MB|KiB))\)", text)
        m = mm.group(1) if mm else None
    p = f"<p>{e(desc)}</p>" if desc and desc != "PDF-Dokument" else ""
    mt = f'<span class="meta">{e(m)}</span>' if m else (f'<span class="meta">PDF</span>' if desc == "PDF-Dokument" else "")
    return (f'<a class="card" href="{e(href)}" target="_blank" rel="noopener">'
            f'{mt}<h3>{e(title)}</h3>{p}</a>')


def cards(items, wide=False):
    cls = "cards cards-wide" if wide else "cards"
    return f'<div class="{cls}">' + "".join(items) + "</div>"


def ul(items, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f"<ul{c}>" + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"


NAV = [
    ("Über uns", None, [("Über uns", "ueber-uns.html"), ("Team", "team.html"), ("Adresse · Anfahrt · Öffnungszeiten", "kontakt.html")]),
    ("Service & Leistungen", None, [("Steuerberatung", "steuerberatung.html"), ("Finanzbuchhaltung", "finanzbuchhaltung.html"),
                                    ("Lohnbuchhaltung", "lohnbuchhaltung.html"), ("Nachfolgeberatung", "nachfolgeberatung.html"),
                                    ("Online-Tools, Downloads, Videos", "service.html")]),
    ("Digitale Kanzlei", "digitale-kanzlei.html", None),
    ("Karriere", "karriere.html", None),
    ("News", "news.html", None),
]
GROUP_OF = {
    "ueber-uns.html": "Über uns", "team.html": "Über uns", "kontakt.html": "Über uns",
    "steuerberatung.html": "Service & Leistungen", "finanzbuchhaltung.html": "Service & Leistungen",
    "lohnbuchhaltung.html": "Service & Leistungen", "nachfolgeberatung.html": "Service & Leistungen",
    "service.html": "Service & Leistungen",
}


def nav_html(current):
    group = GROUP_OF.get(current)
    out = []
    for label, href, subs in NAV:
        if subs:
            on = " is-current" if group == label else ""
            cur = ' aria-current="page"'
            items = "".join(
                f'<li><a href="{h}"{cur if h == current else ""}>{e(t)}</a></li>' for t, h in subs)
            out.append(f'<li class="has-sub"><button type="button" class="sub-toggle{on}" aria-expanded="false" '
                       f'aria-haspopup="true">{e(label)}<i></i></button><ul class="sub-menu">{items}</ul></li>')
        else:
            on = ' class="is-current" aria-current="page"' if href == current else ""
            out.append(f'<li><a href="{href}"{on}>{e(label)}</a></li>')
    out.append(f'<li class="nav-portal"><a href="{PORTAL}" target="_blank" rel="noopener">Online-Portal</a></li>')
    return "".join(out)


def head(title, desc, current):
    full = NAME if current == "index.html" else f"{title} | Scheuer & Partner"
    return f"""<!DOCTYPE html>
<html lang="de" class="no-js">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>{e(full)}</title>
<meta name="description" content="{e(desc)}" />
<meta name="robots" content="noindex, nofollow" />
<meta name="theme-color" content="#ffffff" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{e(full)}" />
<meta property="og:description" content="{e(desc)}" />
<meta property="og:locale" content="de_DE" />
<meta property="og:site_name" content="{e(NAME)}" />
<link rel="stylesheet" href="fonts/fonts.css" />
<link rel="stylesheet" href="styles.css" />
<link rel="icon" href="favicon.png" type="image/png" />
<link rel="apple-touch-icon" href="favicon.png" />
</head>
<body>
<a class="skip" href="#main">Zum Inhalt springen</a>
<div class="progress" id="progress" aria-hidden="true"></div>

<header class="nav" id="nav">
  <a href="index.html" class="brand" aria-label="{e(NAME)}, Startseite">
    <img src="img/logo-mark.png" alt="" class="brand-mark" width="210" height="165" />
    <span class="brand-word">Scheuer &amp; Partner<small>mbB Steuerberatungsgesellschaft</small></span>
  </a>
  <ul class="nav-links" id="nav-links">{nav_html(current)}</ul>
  <a href="{PORTAL}" target="_blank" rel="noopener" class="btn btn-small nav-cta magnetic">Online-Portal</a>
  <button type="button" class="burger" id="burger" aria-expanded="false" aria-controls="nav-links" aria-label="Menü öffnen"><span></span><span></span><span></span></button>
</header>

<main id="main">
"""


def foot():
    return f"""
</main>

<footer class="footer">
  <div class="footer-inner">
    <div class="footer-brand">
      <img src="img/logo-light.png" alt="{e(NAME)}" class="footer-logo" width="1089" height="467" />
      <address>In den Freßäckern 10<br />74321 Bietigheim-Bissingen<br />Deutschland<br />
        <a href="tel:+49714270000">07142 7000-0</a><a href="mailto:{MAIL}">{MAIL}</a></address>
    </div>
    <div>
      <h4>Kanzlei</h4>
      <a href="ueber-uns.html">Über uns</a>
      <a href="team.html">Team</a>
      <a href="kontakt.html">Adresse · Anfahrt</a>
      <a href="karriere.html">Karriere</a>
      <a href="news.html">News</a>
    </div>
    <div>
      <h4>Leistungen</h4>
      <a href="steuerberatung.html">Steuerberatung</a>
      <a href="finanzbuchhaltung.html">Finanzbuchhaltung</a>
      <a href="lohnbuchhaltung.html">Lohnbuchhaltung</a>
      <a href="nachfolgeberatung.html">Nachfolgeberatung</a>
      <a href="digitale-kanzlei.html">Digitale Kanzlei</a>
    </div>
    <div>
      <h4>Rechtliches</h4>
      <a href="impressum.html">Impressum</a>
      <a href="datenschutz.html">Datenschutz</a>
      <a href="sitemap.html">Sitemap</a>
      <a href="{PORTAL}" target="_blank" rel="noopener">Online-Portal</a>
    </div>
  </div>
  <div class="footer-bottom"><small>© 2026 {e(NAME)}</small></div>
</footer>

<a class="sticky-cta" href="kontakt.html" id="sticky-cta">Kontakt aufnehmen</a>
<script src="vendor/gsap.min.js"></script>
<script src="vendor/ScrollTrigger.min.js"></script>
<script src="vendor/lenis.min.js"></script>
<script src="script.js"></script>
</body>
</html>
"""


def write(name, content):
    (ROOT / name).write_text(content, encoding="utf-8")
    print("geschrieben", name, len(content) // 1024, "KB")


CTA_CONTACT = """
  <section class="cta" id="kontakt">
    <div class="cta-bars" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i></div>
    <div class="cta-inner">
      <p class="kicker reveal" style="justify-content:center">Kontakt</p>
      <h2 data-split>So finden Sie uns</h2>
      <p class="reveal">Hier finden Sie unsere Adressdaten und Bürozeiten. Besuchen Sie unsere Kanzlei! Wir nehmen uns gerne Zeit für Sie.</p>
      <div class="cta-buttons reveal">
        <a href="tel:+49714270000" class="btn btn-lg magnetic">07142 7000-0 anrufen</a>
        <a href="mailto:mail@scheuer-partner.de" class="btn btn-ghost btn-lg">E-Mail schreiben</a>
      </div>
    </div>
  </section>
"""


def subpage(slug, title, desc, h1, lead, crumbs, photo, body, alt_photo="", cta=True):
    cr = ['<li><a href="index.html">Startseite</a></li>']
    for label, href in crumbs:
        cr.append(f'<li><a href="{href}">{e(label)}</a></li>' if href else f'<li aria-current="page">{e(label)}</li>')
    lead_html = f'<p class="lead">{e(lead)}</p>' if lead else ""
    page = head(title, desc, slug)
    page += f"""
  <div class="page-head">
    <ol class="crumbs" aria-label="Pfad">{''.join(cr)}</ol>
    <h1>{e(h1)}</h1>
    {lead_html}
  </div>
  <div class="page-photo"><img src="img/{photo}" alt="{e(alt_photo)}" width="1600" height="900" fetchpriority="high" /></div>
"""
    page += body
    if cta:
        page += CTA_CONTACT
    page += foot()
    write(slug, page)


def section(inner, alt=False, sid=""):
    i = f' id="{sid}"' if sid else ""
    cls = "section section-alt cut-top" if alt else "section"
    return f'\n  <section class="{cls}"{i}>\n{inner}\n  </section>\n'


def shead(kicker, h2, sub=""):
    s = f'<p class="sub">{e(sub)}</p>' if sub else ""
    return f'<div class="section-head reveal"><p class="kicker">{e(kicker)}</p><h2 data-split>{e(h2)}</h2>{s}</div>'


# ---------------------------------------------------------------------------
# Startseite
# ---------------------------------------------------------------------------
def index():
    p = head("Startseite", "Scheuer & Partner mbB Steuerberatungsgesellschaft in Bietigheim-Bissingen: Steuerberatung, Finanzbuchhaltung, Lohnbuchhaltung und Nachfolgeberatung seit über 60 Jahren.", "index.html")
    tiles = [
        ("01", "Steuerberatung", "steuerberatung.html", "Die Anforderungen an eine moderne Steuerberatung sind einem permanenten Wandel unterworfen."),
        ("02", "Finanzbuchhaltung", "finanzbuchhaltung.html", "Dies ist die Basis für Ihr Unternehmen."),
        ("03", "Lohnbuchhaltung", "lohnbuchhaltung.html", "Die Anforderungen im Personalbereich steigen ständig."),
        ("04", "Nachfolgeberatung", "nachfolgeberatung.html", "Bei der Definition einer Unternehmensnachfolge sind zahlreiche Aspekte zu behandeln."),
    ]
    tile_html = "".join(
        f'<a class="tile reveal" href="{h}"><span class="tile-n">{n}</span><h3>{e(t)}</h3><p>{e(d)}</p><span class="go">Mehr erfahren</span></a>'
        for n, t, h, d in tiles)
    p += f"""
  <section class="hero" id="top">
    <figure class="hero-media">
      <img src="img/hero.jpg" alt="Das Enzviadukt in Bietigheim-Bissingen" width="1600" height="1066" fetchpriority="high" />
      <span class="hero-wipe" aria-hidden="true"></span>
    </figure>

    <div class="hero-inner">
      <p class="eyebrow reveal">Steuerberatungsgesellschaft <span class="keep-case">mbB</span></p>
      <div class="hero-title-zoom">
        <h1 class="hero-title"><span class="line"><span>Scheuer</span></span><span class="line accent"><span>&amp; Partner</span></span></h1>
        <span class="title-rule" aria-hidden="true"></span>
      </div>
      <p class="lead reveal">Die Anliegen unserer Mandanten sind vielschichtig und umfangreich. Nur ein kompetentes Team kann diese lösen und jeder Einzelne trägt seinen Teil dazu bei.</p>
      <div class="hero-cta reveal">
        <a href="ueber-uns.html" class="btn btn-lg magnetic">Mehr erfahren</a>
        <a href="#kontakt" class="btn btn-ghost btn-lg">Kontakt</a>
      </div>
    </div>

    <dl class="stats reveal">
      <div class="stat"><dt>Gegründet</dt><dd data-count="1961" data-from="1900">1961</dd></div>
      <div class="stat"><dt>Seit über</dt><dd data-count="60" data-from="0" data-suffix=" Jahren">60 Jahren</dd></div>
      <div class="stat"><dt>Im Team</dt><dd data-count="30" data-from="0" data-prefix="rund ">rund 30</dd></div>
      <div class="stat"><dt>Leistungen</dt><dd data-count="4" data-from="0" data-suffix=" Bereiche">4 Bereiche</dd></div>
    </dl>
  </section>

  <div class="marquee" aria-hidden="true">
    <div class="marquee-track" id="marquee-track" data-words="Steuerberatung|Finanzbuchhaltung|Lohnbuchhaltung|Nachfolgeberatung|Digitale Kanzlei"></div>
  </div>
"""
    p += section(f"""    <div class="section-head reveal">
      <p class="kicker">Service &amp; Leistungen</p>
      <h2 data-split>Unsere Leistungen</h2>
      <p class="sub">Jede Entscheidung hat immer auch wirtschaftliche, steuerliche und rechtliche Folgen. Bei Unternehmen genauso wie bei Privatpersonen. Wir arbeiten daher interdisziplinär und bieten Ihnen ein Gesamtpaket:</p>
    </div>
    <div class="tiles">{tile_html}</div>""", sid="leistungen")

    p += section("""    <div class="split">
      <figure class="media media-a reveal">
        <img src="img/kopf-ueber-uns.jpg" alt="Häuser an der Enz in der Altstadt von Bietigheim" loading="lazy" width="1600" height="1066" style="aspect-ratio:4/3;object-fit:cover" />
      </figure>
      <div>
        <p class="kicker reveal">Über uns</p>
        <h2 data-split>Seit 1961 an Ihrer Seite</h2>
        <p class="reveal">Generalistenwissen vereint sich dabei mit Spezialisten-Know-how. Unsere Beratung ist umsetzungsorientiert und unternehmerisch geprägt. Wir entwickeln Lösungen, die maßgeschneidert zu Ihnen passen. Dann setzen wir die Lösungen zusammen mit Ihnen um. Dies machen wir schon seit über 60 Jahren.</p>
        <p class="reveal">Die Kanzlei hat sich als kompetenter Berater in der Region einen Namen gemacht. Seit nunmehr über 60 Jahren liegt unsere Stärke in der interdisziplinären Ausrichtung.</p>
        <p class="reveal"><a class="arrow-link" href="ueber-uns.html">Über uns</a> &nbsp; <a class="arrow-link" href="team.html">Der richtige Ansprechpartner</a></p>
      </div>
    </div>""", alt=True, sid="kanzlei")

    p += section("""    <div class="split flip">
      <div>
        <p class="kicker reveal">Karriere</p>
        <h2 data-split>Ihre Karriere bei uns</h2>
        <p class="reveal">Wir unterstützen seit über 60 Jahren erfolgreich mittelständische Unternehmen und Privatkunden im Bereich Steuern und Buchführung. In unserer Kanzlei setzen wir neben Fachkompetenz auf eine familiäre Atmosphäre und flache Hierarchien.</p>
        <ul class="jobs reveal">
          <li>Finanzbuchhalter (m/w/d)</li>
          <li>Lohnbuchhalter (m/w/d)</li>
          <li>Steuerfachangestellter (m/w/d)</li>
        </ul>
        <p class="reveal"><a class="arrow-link" href="karriere.html">Zur Karriereseite</a></p>
      </div>
      <figure class="media media-b reveal">
        <img src="img/karriere-teaser.jpg" alt="Eine Radfahrerin auf dem Weg zur Arbeit" loading="lazy" width="700" height="1000" />
      </figure>
    </div>""", sid="karriere")

    p += section("""    <div class="split">
      <div>
        <p class="kicker reveal">Digitale Kanzlei</p>
        <h2 data-split>Digitalisierung</h2>
        <p class="reveal">Vorteile der Digitalisierung: Im Rechnungswesen können in Ihrem Unternehmen Prozesse zunehmend digitalisiert und automatisiert werden. Profitieren Sie von den vielen Möglichkeiten!</p>
        <div class="toolrow reveal">
          <a class="chip" href="service.html#tools">Online-Tools</a>
          <a class="chip" href="service.html#links">Nützliche Links</a>
          <a class="chip" href="service.html#downloads">Downloads</a>
          <a class="chip" href="service.html#videos">Videos</a>
        </div>
        <p class="reveal"><a class="arrow-link" href="digitale-kanzlei.html">Digitale Kanzlei</a></p>
      </div>
      <figure class="media media-c reveal">
        <img src="img/digital-teaser.jpg" alt="Hand an einem Tablet mit Auswertungen und Kennzahlen" loading="lazy" width="1100" height="916" />
      </figure>
    </div>
""" + SKONTO, alt=True, sid="digital")

    p += section(f"""    <div class="section-head reveal">
      <p class="kicker">News</p>
      <h2 data-split>Immer Up-To-Date</h2>
      <p class="sub">Aktuelle Informationen über unsere Kanzlei und News per E-Mail. Unser Newsletter hält Sie stets auf dem aktuellen Stand!</p>
      <p style="margin-top:1.4rem"><a class="btn magnetic" href="{NEWSLETTER}">Newsletter anmelden</a></p>
    </div>
    <div class="news-grid">
      <a class="news-item reveal" href="{NEWS_OKT}" target="_blank" rel="noopener"><span class="meta tile-n">Steuernews für Mandanten</span><h3>Elektronische Führung ergänzender Entgeltunterlagen</h3><p>Befreiungsmöglichkeit der Arbeitgeber endet zum Jahresende 2026</p><span class="go">Lesen Sie mehr</span></a>
      <a class="news-item reveal" href="{NEWS_ARZT}" target="_blank" rel="noopener"><span class="meta tile-n">Steuernews für Ärzte</span><h3>BMF-Schreiben zur Umsatzsteuerbefreiung für ...</h3><p>Das BMF konkretisiert Rahmenbedingungen für Umsatzsteuerbefreiung ästhetischer Behandlungen</p><span class="go">Lesen Sie mehr</span></a>
    </div>
    <div class="section-head reveal" style="margin:3rem 0 0">
      <p class="sub" style="margin-top:0">Erfahren Sie laufend aktuelle Informationen sowie steuerliche und gesetzliche Neuerungen!</p>
      <div class="news-links"><a class="chip" href="news.html#mandanten">Steuernews für Mandanten</a><a class="chip" href="news.html#aerzte">Steuernews für Ärzte</a><a class="chip" href="news.html#tv">Steuernews-TV</a></div>
    </div>""", sid="news")

    p += CTA_CONTACT_FULL
    p += foot()
    write("index.html", p)


NEWSLETTER = "mailto:mail@scheuer-partner.de?subject=Anmeldung%20zum%20Newsletter&body=Bitte%20nehmen%20Sie%20mich%20in%20den%20Newsletter-Verteiler%20auf."

SKONTO = """
    <div class="calc reveal" id="skonto">
      <h3>Skonto-Rechner</h3>
      <p class="calc-note">Lohnt es sich mit Skontoabzug zu bezahlen oder nicht? Mit unserem Skonto-Rechner erhalten Sie rasch und mit nur wenigen Klicks Antwort darauf. Die Eingaben verlassen Ihren Browser nicht.</p>
      <div class="calc-grid">
        <div class="field"><label for="c-amount">Rechnungsbetrag in €</label><input id="c-amount" inputmode="decimal" value="5000" /></div>
        <div class="field"><label for="c-pct">Skonto in %</label><input id="c-pct" inputmode="decimal" value="2" /></div>
        <div class="field"><label for="c-early">Skontofrist in Tagen</label><input id="c-early" inputmode="numeric" value="10" /></div>
        <div class="field"><label for="c-term">Zahlungsziel in Tagen</label><input id="c-term" inputmode="numeric" value="30" /></div>
      </div>
      <dl class="calc-out" aria-live="polite">
        <div><dt>Ersparnis</dt><dd id="o-saving">100,00 €</dd></div>
        <div><dt>Zu zahlen</dt><dd id="o-pay">4.900,00 €</dd></div>
        <div><dt>Entspricht</dt><dd class="good" id="o-rate">37,24 % p. a.</dd></div>
      </dl>
      <p class="calc-verdict" id="o-verdict"></p>
    </div>"""

CTA_CONTACT_FULL = """
  <section class="cta" id="kontakt">
    <div class="cta-bars" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i></div>
    <div class="cta-inner" style="max-width:940px">
      <p class="kicker reveal" style="justify-content:center">Kontakt</p>
      <h2 data-split>So finden Sie uns</h2>
      <p class="reveal">Hier finden Sie unsere Adressdaten und Bürozeiten. Besuchen Sie unsere Kanzlei! Wir nehmen uns gerne Zeit für Sie.</p>
      <div class="contact-grid reveal" style="text-align:left;margin-top:2.4rem">
        <div class="box">
          <h3>Scheuer &amp; Partner mbB Steuerberatungsgesellschaft</h3>
          <address>In den Freßäckern 10<br />74321 Bietigheim-Bissingen<br />Deutschland<br /><br />
            Telefon <a href="tel:+49714270000">07142 7000-0</a><br />
            Fax 07142 7000-99<br />
            <a href="mailto:mail@scheuer-partner.de">mail@scheuer-partner.de</a></address>
        </div>
        <div class="box" id="hours">
          <span class="open-badge" id="open-badge">Bürozeiten</span>
          <h3>Bürozeiten</h3>
          <table class="hours"><tbody>
            <tr data-days="1-4"><th>Montag bis Donnerstag</th><td>8 bis 12 Uhr, 13 bis 16 Uhr</td></tr>
            <tr data-days="5-5"><th>Freitag</th><td>8 bis 12 Uhr</td></tr>
          </tbody></table>
          <p>Besprechungstermine nach Vereinbarung</p>
        </div>
      </div>
      <div class="cta-buttons reveal">
        <a href="tel:+49714270000" class="btn btn-lg magnetic">Anrufen</a>
        <a href="mailto:mail@scheuer-partner.de" class="btn btn-ghost btn-lg">E-Mail schreiben</a>
        <a href="kontakt.html" class="btn btn-ghost btn-lg">Anfahrt</a>
      </div>
    </div>
  </section>
"""


# ---------------------------------------------------------------------------
# Unterseiten: Über uns, Team, Kontakt
# ---------------------------------------------------------------------------
def ueber_uns():
    tl = [("1961", "Gründung in Besigheim"), ("1962", "Umzug nach Bietigheim"), ("1965", "Umzug nach Bissingen"),
          ("2005", "Einbringung der Kanzlei in die Partnerschaftsgesellschaft Scheuer & Partner durch Roland Scheuer"),
          ("2011", "Aufnahme von Frau Sandra Häusser als Partnerin"), ("2026", "Aufnahme von Frau Jasmin Titscher als Partnerin")]
    tl_html = "".join(f"<li><h3>{y}</h3><p>{e(t)}</p></li>" for y, t in tl)
    body = section(f"""    <div class="split">
      <div>
        <p class="kicker reveal">Geschichte</p>
        <h2 data-split>Seit über 60 Jahren</h2>
        <p class="reveal">Roland Scheuer gründete im April 1961 in Besigheim eine Steuerkanzlei. Seit 1965 befindet sich die Kanzlei in den heutigen Räumen in Bietigheim-Bissingen. Im Januar 2005 brachte Roland Scheuer seine Kanzlei in die Partnerschaftsgesellschaft Scheuer &amp; Partner ein, deren Partner er weiterhin war.</p>
        <p class="reveal">Die Kanzlei hat sich als kompetenter Berater in der Region einen Namen gemacht. Seit nunmehr über 60 Jahren liegt unsere Stärke in der interdisziplinären Ausrichtung. Dies ermöglicht uns passende Lösungen in den Bereichen Steuerberatung, Bilanzierung und betriebswirtschaftliche Beratung zu erarbeiten und umzusetzen. Mit gleichem Engagement beraten wir im Rahmen der Finanzplanung und in wirtschaftsrechtlichen Fragen.</p>
      </div>
      <ol class="timeline reveal">{tl_html}</ol>
    </div>""")
    body += section("""    <div class="split flip">
      <div>
        <p class="kicker reveal">Das Team</p>
        <h2 data-split>Rund 30 Personen</h2>
        <p class="reveal">Rund 30 Personen sind in unserer Kanzlei tätig. Diese Größe lässt genügend Raum für Individualität und führt zur Identifikation mit den Anliegen unserer Mandanten.</p>
        <p class="reveal">Unsere Größe bietet auch das notwendige Potential zur Lösung komplexer und umfangreicher Aufgaben. Ohne Spezialwissen wären diese nicht zu lösen.</p>
        <p class="reveal">Unsere Mandanten verfolgen ehrgeizige Ziele. Letztendlich steht die bestmögliche Beratung von Unternehmern und Privatpersonen im Mittelpunkt unserer Tätigkeit.</p>
      </div>
      <div class="box reveal">
        <h3>Der richtige Ansprechpartner</h3>
        <p>Unsere Ansprechpartner stellen sich vor. Sie beraten und unterstützen Sie gerne in steuerlichen Angelegenheiten. Kontaktieren Sie uns einfach! Wir sind gerne für Sie da!</p>
        <p style="margin-top:1rem"><a class="btn magnetic" href="team.html">Jetzt kontaktieren</a></p>
        <h3 style="margin-top:2rem">So finden Sie uns</h3>
        <p>Hier finden Sie unsere Adressdaten und Bürozeiten. Besuchen Sie unsere Kanzlei! Wir nehmen uns gerne Zeit für Sie.</p>
        <p style="margin-top:1rem"><a class="btn btn-ghost" href="kontakt.html">Adresse und Anfahrt</a></p>
      </div>
    </div>""", alt=True)
    subpage("ueber-uns.html", "Über uns", "Seit 1961 an Ihrer Seite: Geschichte, Größe und Ausrichtung der Kanzlei Scheuer & Partner in Bietigheim-Bissingen.",
            "Über uns", "", [("Über uns", None)], "kopf-ueber-uns.jpg", body, "Häuser an der Enz in der Altstadt von Bietigheim")


PEOPLE = [
    ("Eva", "Scheuer", "ES", "Steuerberaterin, Rechtsanwältin, Fachanwältin für Steuerrecht, Mitglied des Stiftungsrats Stiftung für die Diakoniestation Bietigheim-Bissingen, Vorstandsmitglied der Stiftung Evangelische Hochschule Ludwigsburg",
     "e.scheuer@scheuer-partner.de",
     ["Steuerliche Gestaltungsberatung", "Rechtsbehelfe und Rechtsmittel (einschließlich Vertretung vor den Finanzgerichten und dem Bundesfinanzhof)", "Kommunen", "Stiftungen", "Vertragsrecht"]),
    ("Sandra", "Häusser", "SH", "Dipl.-Betriebswirtin (BA) Steuerberaterin", "s.haeusser@scheuer-partner.de",
     ["Existenzgründungsberatung", "Unternehmensumstrukturierungen", "steuerliche Beratung von natürlichen Personen und Unternehmen", "betriebswirtschaftliche Beratung", "steuerliche Gestaltung und Planung"]),
    ("Jasmin", "Titscher", "JT", "Steuerberaterin", "j.titscher@scheuer-partner.de",
     ["Jahresabschluss Handels- und Steuerrecht", "Steuererklärungen", "steuerliche Beratung von natürlichen Personen und Unternehmen", "betriebswirtschaftliche Beratung, Planung und Gestaltung"]),
]


def team():
    cards_ = []
    for first, last, mono, role, mail, foci in PEOPLE:
        name = f"{first} {last}" if first != "Sandra" else "Dipl.-Betriebswirtin (BA) Sandra Häusser"
        r = role if first != "Sandra" else "Steuerberaterin"
        cards_.append(f"""<article class="person reveal">
        <span class="monogram" aria-hidden="true">{mono}</span>
        <h3>{e(name)}</h3>
        <p class="role">{e(r)}</p>
        <h4>Schwerpunkte</h4>
        {ul(foci)}
        <div class="contact">
          <a href="tel:+49714270000">07142 7000-0</a>
          <a href="mailto:{mail}">{mail}</a>
        </div>
        <div class="btn-row">
          <a class="btn btn-small" href="tel:+49714270000">Anrufen</a>
          <button type="button" class="btn btn-small btn-ghost vcard" data-first="{e(first)}" data-last="{e(last)}" data-title="{e(r.split(',')[0])}" data-mail="{mail}">Kontakt speichern</button>
        </div>
      </article>""")
    body = section(f"""    <p class="intro reveal" style="margin-bottom:2.6rem">Ihre Ansprechpartner sind jederzeit für Sie da und beraten Sie gerne in steuerlichen Fragen. Kontaktieren Sie uns einfach! Wir freuen uns auf Ihren Besuch!</p>
    <div class="team">{''.join(cards_)}</div>""")
    subpage("team.html", "Team", "Die Ansprechpartnerinnen der Kanzlei Scheuer & Partner mit ihren Schwerpunkten.", "Team", "",
            [("Über uns", "ueber-uns.html"), ("Team", None)], "kopf-ueber-uns.jpg", body, "Häuser an der Enz in der Altstadt von Bietigheim")


def kontakt():
    body = section(f"""    <div class="contact-grid">
      <div class="box reveal">
        <h3>Scheuer &amp; Partner mbB Steuerberatungsgesellschaft</h3>
        <address>In den Freßäckern 10<br />74321 Bietigheim-Bissingen<br />Deutschland<br /><br />
          Telefon <a href="tel:+49714270000">07142 7000-0</a><br />
          Fax 07142 7000-99<br />
          <a href="mailto:mail@scheuer-partner.de">mail@scheuer-partner.de</a></address>
        <p style="margin-top:1.4rem;display:flex;flex-wrap:wrap;gap:.6rem">
          <a class="btn btn-small" href="tel:+49714270000">Anrufen</a>
          <a class="btn btn-small btn-ghost" href="mailto:mail@scheuer-partner.de">E-Mail</a>
        </p>
      </div>
      <div class="box reveal" id="hours">
        <span class="open-badge" id="open-badge">Bürozeiten</span>
        <h3>Bürozeiten</h3>
        <table class="hours"><tbody>
          <tr data-days="1-4"><th>Montag bis Donnerstag</th><td>8 bis 12 Uhr, 13 bis 16 Uhr</td></tr>
          <tr data-days="5-5"><th>Freitag</th><td>8 bis 12 Uhr</td></tr>
        </tbody></table>
        <p>Besprechungstermine nach Vereinbarung</p>
      </div>
    </div>
    <div class="box reveal" style="margin-top:clamp(1.4rem,3vw,2.6rem)">
      <h3>So kommen Sie zu uns</h3>
      <p>In den Freßäckern 10, 74321 Bietigheim-Bissingen. Die Karte laden wir nicht automatisch, damit beim Aufruf dieser Seite keine Daten an Dritte gehen. Mit einem Klick öffnet sich die Routenplanung in einem neuen Tab.</p>
      <p style="margin-top:1.2rem;display:flex;flex-wrap:wrap;gap:.6rem">
        <a class="btn" href="{MAPS}" target="_blank" rel="noopener">Route in Google Maps</a>
        <a class="btn btn-ghost" href="{OSM}" target="_blank" rel="noopener">Karte in OpenStreetMap</a>
      </p>
    </div>""")
    subpage("kontakt.html", "Adresse, Anfahrt, Öffnungszeiten", "Anschrift, Telefon, E-Mail und Bürozeiten der Kanzlei Scheuer & Partner in Bietigheim-Bissingen.",
            "Adresse · Anfahrt · Öffnungszeiten", "", [("Über uns", "ueber-uns.html"), ("Adresse", None)], "kopf-ueber-uns.jpg", body,
            "Häuser an der Enz in der Altstadt von Bietigheim", cta=False)


# ---------------------------------------------------------------------------
# Leistungen
# ---------------------------------------------------------------------------
def infos(page, items, title="Informationen"):
    return f'<h2 class="group-title reveal" style="font-size:clamp(1.4rem,2.6vw,1.9rem);max-width:none">{e(title)}</h2>' + \
        cards([card(page, t, n, i) for t, n, *i in [(x[0], x[1], *(x[2:3])) for x in items]])


def info_cards(page, items):
    out = []
    for it in items:
        t, n = it[0], it[1]
        nth = it[2] if len(it) > 2 else 0
        out.append(card(page, t, n, nth))
    return cards(out)


VID_INTRO = "Zum Lesen keine Zeit? Wir bringen komplexes Fachwissen auf den Punkt. Klicken, zurücklehnen und erfahren, was bei Rechnungen, Unternehmensgründung oder Firmenfahrzeugen zu beachten ist."


def gt(txt):
    return f'<h2 class="group-title reveal" style="max-width:none;width:auto">{e(txt)}</h2>'


def leistung(slug, h1, lead, extra_intro, blocks, desc):
    body = ""
    if extra_intro:
        body += section(f'    <p class="intro reveal">{e(extra_intro)}</p>' + blocks[0]) if False else ""
    inner = ""
    if extra_intro:
        inner += f'<p class="intro reveal" style="margin-bottom:2.4rem">{e(extra_intro)}</p>'
    inner += "".join(blocks)
    body = section(inner)
    subpage(slug, h1, desc, h1, lead, [("Service & Leistungen", "steuerberatung.html"), (h1, None)], "kopf-leistungen.jpg", body,
            "Hand an einem Tablet mit Auswertungen und Kennzahlen")


def leistungen():
    # Steuerberatung
    sb = []
    for h, p_, items in (
        ("Steuergestaltung", "Passt die Steuerminimierung zur Unternehmenssituation? Welche Bilanzierungsstrategien sind sinnvoll? Wie sieht eine steueroptimierte Unternehmensnachfolge aus? Was ist bei Erbfolge und Schenkungen zu beachten? Dies sind Fragen, auf die wir Antworten geben. Wir erstellen maßgeschneiderte Gestaltungskonzepte. Steuerberater und Rechtsanwälte zusammen. Nicht nur in der Rückschau sondern für die Zukunft.",
         ["Gutachten zu steuerrechtlichen Fragestellungen", "Beratung bei der Rechtsformwahl", "Individuelle Steuerplanung", "Gestaltung von Unternehmensübertragungen", "Steuergestaltung bei Unternehmensreorganisationen", "Steuerliche Konzeption der Finanzierung in Unternehmen und im Privatbereich"]),
        ("Steuerdeklaration und laufende Beratung", "Laufende Beratung fängt nicht erst bei der Jahresabschlusserstellung an. Sie werden von uns laufend über Änderungen informiert. Nicht erst, wenn Sie fragen. Wir sind der Überzeugung das ist effizienter. Gesetzesänderungen, neue Gerichtsurteile oder Verwaltungsvorschriften erfahren Sie aus unseren Mandantenrundschreiben, aber auch direkt von Ihrem Berater. Dadurch können wir uns zusammen mit Ihnen auf neue Entwicklungen rechtzeitig einstellen.",
         ["Ausarbeitung von Steuererklärungen", "Prüfung von Steuerbescheiden", "Beratung bei Fragen zum Jahresabschluss und zum Bilanzsteuerrecht", "Teilnahme an Betriebsprüfungen und an Schlussbesprechungen", "Beratung bei Umsatzsteuer-Sonderprüfungen", "Umsatzsteuervergütung im In- und Ausland"])):
        sb.append(f'<div class="box reveal"><h3>{e(h)}</h3><p>{e(p_)}</p>{ul(items, "checklist")}</div>')
    P = "steuerberatung"
    blocks = ['<div class="contact-grid">' + "".join(sb) + "</div>",
              gt("Informationen"), info_cards(P, [("FAQ – Steuern", "faq_steuern"), ("Steuerlexikon", "steuerlexikon"),
                                                   ("FAQ – Rechtsformgestaltung", "faq_rechtsform"), ("FAQ - Kfz", "faq_kfz")]),
              gt("Downloads"), cards([card(P, "Checkliste Einkommensteuer (< 1MB)", "checkliste", 0, "Download")], False)]
    leistung("steuerberatung.html", "Steuerberatung",
             "Die Anforderungen an eine moderne Steuerberatung sind einem permanenten Wandel unterworfen. Wie stelle ich die Weichen, damit mein Unternehmen wettbewerbsfähig bleibt? Wie sichere ich mein Vermögen für die Zukunft? Wir weisen Ihnen den Weg durch das zunehmend komplexer werdende Steuerrecht. Ihre Steuerlast zu minimieren ist unser Ziel. Im Sinne einer ganzheitlichen Lösung verlieren wir aber nicht Ihre Rahmenbedingungen aus den Augen (z. B. Unternehmensstruktur, Vermögensverhältnisse).",
             "", blocks, "Steuerberatung und Erstellung von Jahresabschlüssen: Steuergestaltung, Steuerdeklaration und laufende Beratung bei Scheuer & Partner.")

    # Finanzbuchhaltung
    P = "finanzbuchhaltung"
    blocks = [gt("Informationen"), info_cards(P, [("FAQ – Finanzbuchhaltung", "faq_finanzbuchhaltung/"), ("Rechnungsmerkmale", "finanzbuchhaltung/rechnungsmerkmale"),
                                                   ("Aufbewahrungspflichten und -fristen", "aufbewahrung"), ("Fahrtenbuch", "finanzbuchhaltung/fahrtenbuch"),
                                                   ("Kassenbuch", "finanzbuchhaltung/kassenbuch"), ("GoBD", "gobd")]),
              gt("Downloads"), cards([card(P, "Reisekostenabrechnung (< 1MB)", "reisekosten", 0, "Download")]),
              gt("Infovideos"), f'<p class="intro">{e(VID_INTRO)}</p><div style="height:1.4rem"></div>',
              info_cards(P, [("Fahrtenbuch", "infovideos/fahrtenbuch"), ("Kassenbuch", "infovideos/kassenbuch"), ("Rechnungsmerkmale", "infovideos/rechnungsmerkmale"),
                             ("Steuerfreie Lohnbestandteile für Arbeitnehmer", "infovideos/steuerfreie")])]
    leistung("finanzbuchhaltung.html", "Finanzbuchhaltung",
             "Dies ist die Basis für Ihr Unternehmen. Die Finanzbuchhaltung und Jahresabschlusserstellung ermöglichen die finanzielle und betriebswirtschaftliche Standortbestimmung. Darauf basieren weitere wichtige Entscheidungen für Ihr Unternehmen. Die betriebswirtschaftlichen Auswertungen sind individuell auf unsere Mandanten zugeschnitten.",
             "Wir gehen aber noch einen Schritt weiter: Wir bereiten den Jahresabschluss ausführlich im Rahmen einer Präsentation auf. Sie verstehen dadurch Ihr Unternehmen besser und die Analyse zeigt Verbesserungspotentiale auf.",
             blocks, "Finanzbuchhaltung und Jahresabschlusserstellung bei Scheuer & Partner: die Basis für Ihr Unternehmen.")

    # Lohnbuchhaltung
    P = "lohnbuchhaltung"
    blocks = [gt("Informationen"), info_cards(P, [("FAQ – Lohnbuchhaltung", "faq_lohnbuchhaltung"), ("FAQ – Homeoffice", "faq_homeoffice"),
                                                   ("Steuerermäßigung bei haushaltsnahen Tätigkeiten", "steuerermaessigung"), ("Steuerfreie Lohnbestandteile für Arbeitnehmer", "lohnbuchhaltung/steuerfreie"),
                                                   ("Der gesetzliche Mindestlohn", "der_gesetzliche"), ("Reisekostensätze – Länderübersicht", "reisekostensaetze"),
                                                   ("Reisekostenrecht", "reisekostenrecht")]),
              gt("Onlineformulare"), info_cards(P, [("Online Mitarbeiter Abmeldung", "abmeldung"), ("Online Mitarbeiter Änderung", "aenderung"),
                                                     ("Online Neueinstellung Minijob", "anmeldung_minijob"), ("Online Neueinstellungsbogen", "dienstnehmer/anmeldung?"),
                                                     ("Online Sofortmeldung", "sofortmeldung")]),
              gt("Infovideos"), f'<p class="intro">{e(VID_INTRO)}</p><div style="height:1.4rem"></div>',
              info_cards(P, [("Steuerfreie Lohnbestandteile für Arbeitnehmer", "infovideos/steuerfreie")])]
    leistung("lohnbuchhaltung.html", "Lohnbuchhaltung",
             "Die Anforderungen im Personalbereich steigen ständig. Permanente Änderungen gesetzlicher Vorschriften stellen große Herausforderungen dar. Wir verstehen Lohnbuchhaltung nicht als Routinegeschäft, sondern betreuen unsere Mandanten individuell. Von der monatlichen Lohnabrechnung bis hin zu Spezialfragen. Wir übernehmen auf Wunsch auch den gesamten Zahlungsverkehr in diesem Bereich.",
             "Natürlich umfasst unsere Beratung auch alle Fragen im Bereich Sozialversicherung. Angefangen bei Beitragssätzen zur Krankenversicherung bis hin zur Beurteilung der betrieblichen Altersvorsorge. Sowohl in wirtschaftlicher als auch in rechtlicher Hinsicht.",
             blocks, "Lohnbuchhaltung bei Scheuer & Partner: von der monatlichen Lohnabrechnung bis zu Spezialfragen und Sozialversicherung.")

    # Nachfolgeberatung
    P = "nachfolgeberatung"
    blocks = ['<div class="box reveal"><h3>Unser Leistungsangebot</h3>' + ul(["Beratung zu Steuerthemen", "Beratung zur finanziellen Sicherheit im Ruhestand", "Beratung zur Sicherung des Fortbestands Ihres Unternehmens"]).replace("<ul>", '<ul class="jobs">') + "</div>",
              gt("Informationen"), info_cards(P, [("Schenkungsteuer", "schenkungsteuer"), ("Vermögensübertragung auf Kinder", "vermoegensuebertragung"), ("Rechtsformvergleich", "rechtsformvergleich")])]
    leistung("nachfolgeberatung.html", "Nachfolgeberatung",
             "Bei der Definition einer Unternehmensnachfolge sind zahlreiche Aspekte zu behandeln. Sie können das Know-how unserer Spezialisten dafür nützen, Ihre Unternehmensnachfolge optimal und wie gewünscht über die Bühne zu bringen.",
             "", blocks, "Nachfolgeberatung bei Scheuer & Partner: Steuern, Ruhestand und Fortbestand Ihres Unternehmens.")


# ---------------------------------------------------------------------------
# Digitale Kanzlei, Service, Karriere, News
# ---------------------------------------------------------------------------
def digitale_kanzlei():
    P = "digitale-kanzlei"
    body = section(
        gt("Informationen") +
        info_cards(P, [("Elektronische Rechnungen – Praxistipps", "elektronische_rechnungen"), ("ADDISON OneClick", "addison")]) +
        gt("Online-Rechner") + info_cards(P, [("Digital-Fitness-Check", "digitalfitness")]))
    body += section(SKONTO.replace('<div class="calc reveal"', '<div class="calc reveal"').replace("margin-top:2.4rem", ""), alt=True, sid="rechner")
    subpage("digitale-kanzlei.html", "Digitale Kanzlei", "Digitalisierung im Rechnungswesen: elektronische Rechnungen, ADDISON OneClick und Online-Rechner von Scheuer & Partner.",
            "Digitale Kanzlei",
            "Digitalisierung! Seit Jahren arbeiten wir mit unseren Mandanten auch online zusammen. Nutzen Sie unser Know-how für Ihre Onlinebuchhaltung. Erfahren Sie jetzt mehr.",
            [("Digitale Kanzlei", None)], "kopf-digital.jpg", body, "Ein Team bespricht Unterlagen in einem Büro")


def service():
    T = "online-tools"
    tools = [("Annuitäten-Rechner", "annuitaeten"), ("Betriebliche-Altersvorsorge", "altersvorsorge"), ("Brutto-Netto-Rechner", "brutto_netto"),
             ("Chancen-Rechner", "chancen"), ("Digital-Fitness-Check", "digitalfitness"), ("Einkommensteuer-Rechner", "einkommensteuer"),
             ("Erinnerungsservice", "reminder"), ("Haushalts-Rechner", "haushalt"), ("Lebensstandard-Rechner", "lebensstandard"),
             ("Skonto-Rechner", "skonto"), ("Vermögensbilanz", "vermoegensbilanz")]
    D = "downloads"
    dl_service = [("Checkliste Einkommensteuer (< 1MB)", "checkliste"), ("Reisekostenabrechnung (< 1MB)", "reisekosten")]
    dl_rund = [("Mandanten-Rundschreiben 10-2018 (114KiB)", "10-2018"), ("Mandanten-Rundschreiben 09-2018 (120KiB)", "09-2018"), ("Mandanten-Rundschreiben 08-2018 (119KiB)", "08-2018")]
    dl_frage = [("Fragebogen Nachweis Kinder PV (165KiB)", "downloads8"), ("Personalfragebogen (188KiB)", "Personalfragebogen.pdf"),
                ("Personalfragebogen Minijobs (205KiB)", "Minijobs"), ("Personalfragebogen Kündigung (205KiB)", "Kuendigung"), ("Stundenaufzeichnung MiLoG (103KiB)", "milog")]

    def dcard(title, needle, extra_meta=None):
        href, text = link(D, needle)
        desc = text[len(title):].strip()
        m = re.search(r"\(([^)]+)\)", title)
        clean = re.sub(r"\s*\([^)]*\)", "", title)
        d = f"<p>{e(desc)}</p>" if desc and desc != "PDF-Dokument" else ""
        return f'<a class="card" href="{e(href)}" target="_blank" rel="noopener"><span class="meta">{e(m.group(1) if m else "Download")}</span><h3>{e(clean)}</h3>{d}</a>'

    def vcard_(title, needle, page="videos"):
        href, text = link(page, needle)
        desc = text[len(title):].strip()
        return f'<a class="card" href="{e(href)}" target="_blank" rel="noopener"><h3>{e(title)}</h3><p>{e(desc)}</p></a>'

    tv = [("Oktober 2026: Häusliches Arbeitszimmer: Auf diese Aufzeichnungspflichten ...", "oktober_2026"), ("September 2026: Altersvorsorgereformgesetz: Was ist neu?", "september_2026"),
          ("August 2026: Sind Immobilien-Seminare steuerlich absetzbar?", "august_2026"), ("Juli 2026: BMF-Schreiben bringt Neuerungen beim Ladestrom für E-Autos", "juli_2026")]
    iv = [("Fahrtenbuch", "infovideos/fahrtenbuch"), ("FAQ - Auto", "faq_auto"), ("FAQ - Finanzbuchhaltung", "faq_finanzbuchhaltung"), ("FAQ - Gründungsberatung", "gr"),
          ("Gesetzlicher Mindestlohn", "mindestlohn"), ("Kassenbuch", "kassenbuch"), ("Rechnungsmerkmale", "rechnungsmerkmale"),
          ("Steuerfreie Lohnbestandteile für Arbeitnehmer", "steuerfreie"), ("Steuertipps zum Jahresende", "steuertipps")]
    body = section(f"""
    <div id="tools">
      <div class="section-head reveal"><p class="kicker">Service</p><h2 data-split>Online-Tools</h2>
        <p class="sub">Mithilfe unserer Onlinerechner können Sie sofort für Sie als Unternehmer wesentliche Beträge errechnen! Wählen Sie einfach den gewünschten Rechner aus und starten Sie gleich mit der gewünschten Berechnung!</p></div>
      <h3 class="group-title reveal">Profitieren Sie von unserem Serviceangebot</h3>
      {cards([card(T, t, n) for t, n in tools])}
    </div>""")
    body += section(f"""
    <div id="downloads">
      <div class="section-head reveal"><p class="kicker">Service</p><h2 data-split>Downloads</h2>
        <p class="sub">Achtung: Beim Fragebogen "Kinder" muss die Steuer ID nicht eingetragen werden!</p></div>
      <h3 class="group-title reveal">Profitieren Sie von unserem Serviceangebot</h3>
      {cards([dcard(t, n) for t, n in dl_service] + [dcard("Fragebogen Nachweis Kinder PV (159KiB)", "downloads3")])}
      <h3 class="group-title reveal">Mandantenrundschreiben</h3>
      {cards([dcard(t, n) for t, n in dl_rund])}
      <h3 class="group-title reveal">Hinweise für Mandanten</h3>
      <p class="intro" style="margin-bottom:1.2rem">Diese Hinweise erhalten unsere Mandanten mit der Post.</p>
      {cards([dcard("Hinweise zum Jahreswechsel 2018/2019 (56KiB)", "Jahreswechsel")])}
      <h3 class="group-title reveal">Fragebögen</h3>
      {cards([dcard(t, n) for t, n in dl_frage])}
    </div>""", alt=True)
    body += section(f"""
    <div id="links">
      <div class="section-head reveal"><p class="kicker">Service</p><h2 data-split>Links</h2>
        <p class="sub">Wichtige steuerliche Informationen, Behörden und Förderungen finden Sie im Netz. Nützen Sie diesen Vorteil!</p></div>
      <h3 class="group-title reveal">Nützliche Links</h3>
      {cards([card("links", "Behördenverzeichnis", "beh"), card("links", "Heilberufe", "heilberufe")], True)}
    </div>""")
    body += section(f"""
    <div id="videos">
      <div class="section-head reveal"><p class="kicker">Service</p><h2 data-split>Videos</h2>
        <p class="sub">Mit unseren Kanzlei-Videos können Sie aus einem breiten Videoangebot wählen. Wir bieten Informationsvideos, die steuerlich relevante Themen Schritt für Schritt erklären. Regelmäßig produzieren wir auch professionelle Nachrichtensendungen und berichten über aktuelle Neuigkeiten aus der Steuerwelt.</p></div>
      <h3 class="group-title reveal">Steuernews-TV</h3>
      <p class="intro" style="margin-bottom:1.2rem">Immer aktuell mit unserem Video-Format: Steuernews-TV - immer die neuesten News über steuerliche Änderungen.</p>
      {cards([vcard_(t, n) for t, n in tv], True)}
      <h3 class="group-title reveal">Infovideos</h3>
      <p class="intro" style="margin-bottom:1.2rem">{e(VID_INTRO)}</p>
      {cards([vcard_(t, n) for t, n in iv])}
    </div>""", alt=True)
    subpage("service.html", "Service: Online-Tools, Downloads, Links, Videos", "Online-Rechner, Downloads, nützliche Links und Videos von Scheuer & Partner.",
            "Service", "Online-Tools, Downloads, Links und Videos.", [("Service & Leistungen", "steuerberatung.html"), ("Service", None)], "kopf-leistungen.jpg", body,
            "Hand an einem Tablet mit Auswertungen und Kennzahlen")


def karriere():
    perks = [("Arbeitsklima", "Nur, wer sich wohlfühlt, ist auch motiviert, immer wieder Höchstleistungen für unsere Kunden zu erbringen. Ein angenehmes, freundliches und wertschätzendes Arbeitsklima ist uns daher besonders wichtig und wird aktiv von uns gefördert."),
             ("Einarbeitung/Teamwork", "Teamwork wird bei uns großgeschrieben – und zwar von Anfang an! Bei uns bekommt jeder neue Mitarbeiter eine umfassende Einarbeitung und kann sich auch danach auf seine Kollegen verlassen – denn gemeinsam sind wir stark!"),
             ("Flexible Arbeitszeiten", "Nur, wer gerne und motiviert zur Arbeit kommt, kann Höchstleistungen erbringen. In der Freizeit wieder aufzutanken ist daher für jeden von uns wichtig. Deshalb bieten wir unseren Mitarbeitern flexible Arbeitszeiten, dank denen sie selbst ihren idealen Rhythmus finden können."),
             ("Gute Verkehrsanbindung", "Wer möchte schon auf dem Weg zur Arbeit gestresst werden? Unsere Kanzlei befindet sich in einer sehr günstigen Lage, die dank der hervorragenden Verkehrsanbindung sowohl mit dem KFZ als auch mit den öffentlichen Verkehrsmitteln unkompliziert zu erreichen ist."),
             ("Homeoffice", "Eine ausgeglichene Work-Life-Balance ist uns genauso wichtig wie ein angenehmes Familienleben. Daher bieten wir unseren Mitarbeitern nach Absprache die Möglichkeit, ihre Arbeit von zu Hause aus zu verrichten."),
             ("Kostenfreie Getränke", "Wer einen kühlen Kopf bewahren will, muss ausreichend Flüssigkeit zu sich nehmen. Für uns ist es selbstverständlich, unseren Mitarbeitern eine kostenfreie Auswahl an Getränken zur Verfügung zu stellen."),
             ("Lieferungen Mittagstisch in die Kanzlei", "Gut zu essen ist unerlässlich, wenn man voller Energie durch den Tag kommen will. Wir bieten unseren Mitarbeitern daher einen Mittagstisch mit täglich frischen Gerichten an."),
             ("Mitarbeiter-Events", "Bei uns wird ein gutes Arbeitsklima großgeschrieben und gefördert! Um das Miteinander zu stärken, organisieren wir für unsere Mitarbeiter regelmäßige Aktivitäten und Events, wie Betriebsausflüge und After-Work-Treffen."),
             ("Moderner Arbeitsplatz", "Wir gehen mit der Zeit! Damit wir unsere Kunden zeitgerecht beraten können, ist uns auch ein moderner Arbeitsplatz mit entsprechender Ausstattung sehr wichtig."),
             ("Parkplätze vor dem Haus", "Damit Sie morgens nicht ewig nach einem Parkplatz suchen müssen, sondern stressfrei in den Tag starten können, gibt es bei uns direkt vor der Kanzlei Parkplätze für unsere Mitarbeiter."),
             ("Weiterbildung", "Auf Stillstand haben wir keine Lust! Wir glauben, dass eine persönliche und berufliche Weiterbildung in unserem Berufsstand unerlässlich ist. Denn nur, wer auf dem aktuellen Stand ist, kann auch umfänglich beraten. Daher unterstützen wir das Know-how unserer Mitarbeiter mit regelmäßigen internen wie externen Weiterbildungen.")]
    pk = "".join(f'<div class="perk reveal"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in perks)
    why = [("Beruf oder Familie?", "Ihre Familie liegt uns genauso am Herzen wie Ihre berufliche Weiterentwicklung. Das verstehen wir unter sozialem Engagement. Damit unsere Mitarbeiter sich für Beruf und Familie entscheiden können, bieten wir unterschiedliche Arbeitszeitmodelle an."),
           ("Karrierechancen", "Wir entwickeln uns ständig weiter und mit jedem kompetenten Mitarbeiter mehr wird unser Team noch stärker. Für unsere Mitarbeiter bieten sich Chancen zur beruflichen Weiterentwicklung. Wir wollen weiter wachsen – daher sind wir stets daran interessiert, qualifizierte Mitarbeiter zu gewinnen. Da immer wieder interessante Stellen bei unseren nationalen oder internationalen Partnern vakant werden, freuen wir uns auch auf Ihre Initiativbewerbung. Ein tolles Team und ein Beruf mit Zukunft! Wir bieten Ihnen spannende Aufgaben, eine wertschätzende Unternehmenskultur und ein attraktives Arbeitsumfeld, das Sie mitgestalten können."),
           ("Arbeitszeitmodelle für jede Lebensphase", "Wir fördern die Vereinbarkeit von Beruf und Privatleben und bieten unseren Mitarbeitern auch flexible Arbeitszeitmodelle an. Sowohl Berufseinsteiger als auch Spezialisten mit Erfahrung sind bei uns herzlich willkommen."),
           ("Mit einem starken Team in die Zukunft", "Unsere Mitarbeiter sind offen für neue Herausforderungen und widmen sich ihren Aufgaben mit größter Sorgfalt. So gelingt es uns immer wieder, die Erwartungen unserer Mandanten zu übertreffen. Auch für die Zukunft haben wir richtig viel vor. Wenn Sie zusätzlich zu Ihrem Fachwissen auch Enthusiasmus für Ihren Beruf mitbringen, dann sind Sie bei uns goldrichtig.")]
    wh = "".join(f'<div class="box reveal"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in why)
    body = section(f'<div class="split"><div>{shead("Warum zu uns?", "Warum zu uns?")}<p class="intro reveal">Unser Erfolg beruht vor allem auf dem Wissen und dem Engagement unserer Mitarbeiter, die Verantwortung suchen und bereit sind, sich täglich neuen Anforderungen und Aufgaben zu stellen.</p><p class="intro reveal">Bei uns haben Sie die Möglichkeit, sich und Ihr Können einzubringen – egal, ob während des Studiums, nach dem Hochschulabschluss oder mit beruflichen Erfahrungen.</p></div>'
                   f'<figure class="media media-b reveal"><img src="img/karriere-teaser.jpg" alt="Eine Radfahrerin auf dem Weg zur Arbeit" loading="lazy" width="700" height="1000" /></figure></div>'
                   f'<div class="contact-grid" style="margin-top:3rem">{wh}</div>', sid="warum")
    body += section(f'{shead("Benefits", "Benefits", "Wir geben als Arbeitgeber unser Bestes und bieten unseren Mitarbeitern ein Package an attraktiven Zusatzleistungen.")}<div class="perks">{pk}</div>', alt=True, sid="benefits")
    body += section(f"""{shead("Offene Stellen", "Offene Stellen", "Wir sind auf der Suche nach engagierten Mitarbeitern, die mit uns gemeinsam unsere Mandanten optimal betreuen und am Erfolg teilhaben wollen. Grundsätzlich richten sich unsere Stellenausschreibungen sowohl an Frauen als auch Männer ohne Altersbeschränkung.")}
    <ul class="jobs reveal" style="max-width:520px"><li>Finanzbuchhalter (m/w/d)</li><li>Lohnbuchhalter (m/w/d)</li><li>Steuerfachangestellter (m/w/d)</li></ul>""", sid="stellen")
    body += section(f"""{shead("Blitzbewerbung", "Sie möchten Teil unseres Teams werden?", "Dann senden Sie uns doch Ihre Initiativbewerbung. Wir freuen uns auf Sie!")}
    <p class="reveal" style="margin-top:-1rem"><a class="btn btn-lg magnetic" href="mailto:{MAIL}?subject=Initiativbewerbung">Bewerbung per E-Mail senden</a></p>""", alt=True, sid="bewerbung")
    subpage("karriere.html", "Karriere", "Karriere bei Scheuer & Partner: Warum zu uns, Benefits, offene Stellen und Initiativbewerbung.", "Karriere",
            "Wir unterstützen seit über 60 Jahren erfolgreich mittelständische Unternehmen und Privatkunden im Bereich Steuern und Buchführung. In unserer Kanzlei setzen wir neben Fachkompetenz auf eine familiäre Atmosphäre und flache Hierarchien.",
            [("Karriere", None)], "kopf-karriere.jpg", body, "Eine Radfahrerin auf dem Weg zur Arbeit", cta=False)


def news():
    body = section(f"""
    <div id="mandanten">{shead("Steuernews für Mandanten", "Steuernews für Mandanten")}
      <div class="news-grid">
        <a class="news-item reveal" href="{NEWS_OKT}" target="_blank" rel="noopener"><h3>Elektronische Führung ergänzender Entgeltunterlagen</h3><p>Befreiungsmöglichkeit der Arbeitgeber endet zum Jahresende 2026</p><span class="go">Lesen Sie mehr</span></a>
        <a class="news-item reveal" href="{OLD}/de/news/steuernews_f%C3%BCr_mandanten/" target="_blank" rel="noopener"><h3>Alle Steuernews für Mandanten</h3><p>Erfahren Sie laufend aktuelle Informationen sowie steuerliche und gesetzliche Neuerungen!</p><span class="go">Zur Übersicht</span></a>
      </div></div>""", sid="")
    body += section(f"""
    <div id="aerzte">{shead("Steuernews für Ärzte", "Steuernews für Ärzte")}
      <div class="news-grid">
        <a class="news-item reveal" href="{NEWS_ARZT}" target="_blank" rel="noopener"><h3>BMF-Schreiben zur Umsatzsteuerbefreiung für ...</h3><p>Das BMF konkretisiert Rahmenbedingungen für Umsatzsteuerbefreiung ästhetischer Behandlungen</p><span class="go">Lesen Sie mehr</span></a>
        <a class="news-item reveal" href="{OLD}/de/news/steuernews_f%C3%BCr_%C3%A4rzte/" target="_blank" rel="noopener"><h3>Alle Steuernews für Ärzte</h3><p>Aktuelle Informationen für Heilberufe.</p><span class="go">Zur Übersicht</span></a>
      </div></div>""", alt=True)
    body += section(f"""
    <div id="tv">{shead("Steuernews-TV", "Steuernews-TV", "Immer aktuell mit unserem Video-Format: Steuernews-TV - immer die neuesten News über steuerliche Änderungen.")}
      <p class="reveal"><a class="btn magnetic" href="service.html#videos">Zu den Videos</a></p></div>""")
    body += section(f"""
    <div id="newsletter">{shead("Newsletter", "Immer Up-To-Date", "Mit unserem kostenlosen Newsletter erhalten Sie aktuelle Informationen per E-Mail zugesandt. Aktuelle Informationen über unsere Kanzlei und News per E-Mail. Unser Newsletter hält Sie stets auf dem aktuellen Stand!")}
      <p class="reveal"><a class="btn btn-lg magnetic" href="{NEWSLETTER}">Newsletter anmelden</a></p></div>""", alt=True)
    subpage("news.html", "News", "Steuernews für Mandanten und Ärzte, Steuernews-TV und Newsletter von Scheuer & Partner.", "News",
            "Erfahren Sie laufend aktuelle Informationen sowie steuerliche und gesetzliche Neuerungen!", [("News", None)], "kopf-news.jpg", body,
            "Aktuelle Steuernews", cta=False)


# ---------------------------------------------------------------------------
# Rechtliches
# ---------------------------------------------------------------------------
def legal(slug, title, inner):
    p = head(title, f"{title} von {NAME}", slug)
    p += f'\n  <article class="legal"><ol class="crumbs" aria-label="Pfad"><li><a href="index.html">Startseite</a></li><li aria-current="page">{e(title)}</li></ol>\n    <h1>{e(title)}</h1>\n{inner}\n  </article>\n'
    p += foot()
    write(slug, p)


def impressum():
    inner = f"""
    <p><span class="todo">Vor dem Livegang von der Kanzlei prüfen lassen. Der Eintrag zu Entwurf und Umsetzung der Webseite ist neu zu füllen.</span></p>
    <h2>{e(NAME)}</h2>
    <address>In den Freßäckern 10<br />74321 Bietigheim-Bissingen<br />Deutschland<br /><br />
      Telefon 07142 7000-0<br />Fax 07142 7000-99<br /><a href="mailto:{MAIL}">{MAIL}</a></address>
    <h3>Vertretungsberechtigt</h3>
    <p>Sandra Häusser, Dipl.-Betriebswirtin (BA), Steuerberaterin<br />Jasmin Titscher, Steuerberater</p>
    <p>Umsatzsteuer-Identifikationsnummer: DE240236851<br />Partnerschaftsregister: Amtsgericht Stuttgart, PR 300017</p>
    <h2>Berufshaftpflichtversicherung</h2>
    <p>Die berufliche Tätigkeit ist abgesichert durch eine Vermögensschaden-Haftpflichtversicherung bei der HDI Versicherung AG, HDI Platz 1, 30659 Hannover, diese gilt EU-weit in Zusammenhang mit den versicherten Risiken.</p>
    <h2>Berufsbezeichnung</h2>
    <p>Die gesetzlichen Berufsbezeichnungen Steuerberater und Rechtsanwalt wurden in der Bundesrepublik Deutschland verliehen. Staat der Zulassung ist die Bundesrepublik Deutschland.</p>
    <h2>Zuständige Aufsichtsbehörde der Rechtsanwälte</h2>
    <address><strong>Rechtsanwaltskammer Stuttgart</strong><br />Königstraße 14<br />70173 Stuttgart<br />Deutschland<br />+49 (711) 222 15-50<br />+49 (711) 222 155-11<br />info@rak-stuttgart.de<br />www.rak-stuttgart.de</address>
    <h2>Berufsrechtliche Regelungen für Rechtsanwälte</h2>
    <ul><li>Bundesrechtsanwaltsordnung (BRAO)</li><li>Berufsordnung (BORA)</li><li>Fachanwaltsordnung (FAO)</li><li>Rechtsanwaltsvergütungsgesetz (RVG)</li><li>Gesetz über die Tätigkeit europäischer Rechtsanwälte in Deutschland (EuRAG)</li><li>Berufsregeln der Rechtsanwälte der Europäischen Union (CCBE Berufsregeln)</li></ul>
    <p>Die Regelungen können bei der Bundesrechtsanwaltskammer unter www.brak.de eingesehen werden.</p>
    <h2>Zuständige Aufsichtsbehörde der Steuerberater</h2>
    <address><strong>Steuerberaterkammer Stuttgart</strong><br />Körperschaft des öffentlichen Rechts<br />Hegelstraße 33<br />70174 Stuttgart<br />Deutschland<br />+49 (711) 619 48-0<br />+49 (711) 619 48-702<br />mail@stbk-stuttgart.de<br />www.stbk-stuttgart.de</address>
    <h2>Berufsrechtliche Regelungen für Steuerberater</h2>
    <ul><li>Steuerberatungsgesetz (StBerG)</li><li>Durchführungsverordnung zum Steuerberatungsgesetz (DVStB)</li><li>Berufsordnung der Bundessteuerberaterkammer (BOStB)</li><li>Steuerberatervergütungsverordnung (StBVV)</li></ul>
    <p>Alle Texte können über die Internetseite der Bundessteuerberaterkammer www.bstbk.de abgerufen werden.</p>
    <h2>Entwurf und Umsetzung der Webseite</h2>
    <p><span class="todo">Angabe zu Entwurf und Umsetzung eintragen (Name, Anschrift, Kontakt). Der bisherige Eintrag nennt Atikon Marketing &amp; Werbung GmbH und gilt für die neue Seite nicht.</span></p>
    <h2>Verwendete Schriften</h2>
    <p>Cormorant Garamond und Inter, beide unter der SIL Open Font License. Die Schriften liegen auf diesem Server, es erfolgt keine Verbindung zu Dritten.</p>
    <h2>Diese Seite wird betrieben durch</h2>
    <address><strong>{e(NAME)}</strong><br />In den Freßäckern 10<br />74321 Bietigheim-Bissingen<br />Deutschland</address>
    <h2>Verantwortlicher im Sinne des § 18 Absatz 2 Medienstaatsvertrag (MStV)</h2>
    <address>Sandra Häusser<br />In den Freßäckern 10<br />74321 Bietigheim-Bissingen</address>
    <h2>Grundlegende Richtung</h2>
    <p>Die Angaben auf dieser Webseite dienen lediglich der allgemeinen Information und sind nicht als Rechts-, Steuer- oder sonstige Fachberatung zu sehen. Die Webseite beinhaltet unpolitische News, die sich mit dem Steuer-, Sozial- und Wirtschaftsrecht beschäftigen und sich vorwiegend an Mandanten der Kanzlei richten.</p>
    <h2>Haftungsausschluss</h2>
    <p>Wir sind bestrebt, die hier angebotenen Informationen nach bestem Wissen und Gewissen vollständig und richtig darzustellen und aktuell zu halten. Dennoch können wir keinerlei Haftung für Schäden übernehmen, die sich aus der Nutzung der angebotenen Informationen ergeben können – auch wenn diese auf die Nutzung von allenfalls unvollständigen bzw. fehlerhaften Informationen zurückzuführen sind.</p>
    <p>Verweise auf fremde Webseiten liegen außerhalb unseres Verantwortungsbereiches. Eine Haftung für die Inhalte von verlinkten Seiten ist ausgeschlossen, zumal wir keinen Einfluss auf Inhalte wie Gestaltung von gelinkten Seiten haben. Für Inhalte von Seiten, auf welche von Seiten dieser Webseiten verwiesen wird, haftet somit allein der Anbieter dieser fremden Webseiten – niemals jedoch derjenige, der durch einen Link auf fremde Publikationen und Inhalte verweist. Sollten gelinkte Seiten (insbesondere durch Veränderung der Inhalte nach dem Setzen des Links) illegale, fehlerhafte, unvollständige, beleidigende oder sittenwidrige Informationen beinhalten und wir auf derartige Inhalte von gelinkten Seiten aufmerksam (gemacht) werden, so werden wir einen Link auf derartige Seiten unverzüglich unterbinden.</p>
    <h2>Urheberrecht</h2>
    <p>Die vom Autor selbst erstellten Inhalte (Texte und Bilder) dieser Seiten sind urheberrechtlich geschützt. Die Informationen sind nur für die persönliche Verwendung bestimmt. Jede den Bestimmungen des Urheberrechtsgesetzes widersprechende Verwendung jeglicher Inhalte dieser Webseiten – insbesondere die weitergehende Nutzung wie beispielsweise die Veröffentlichung, Vervielfältigung und jede Form von gewerblicher Nutzung sowie die Weitergabe an Dritte – auch in Teilen oder in überarbeiteter Form – ohne ausdrückliche Zustimmung des Autors ist untersagt.</p>
    <h2>Informationsinhalt</h2>
    <p>Die Informationen dieser Webseiten können ohne vorherige Ankündigung geändert, entfernt oder ergänzt werden. Der Autor kann daher keine Garantie für die Korrektheit, Vollständigkeit, Qualität oder Aktualität der bereitgestellten Informationen geben.</p>
    <h2>Rechtswirksamkeit</h2>
    <p>Durch Nutzung dieser Webseiten unterliegt der Nutzer den gegenständlichen Nutzungsbedingungen. Diese sind Teil des WWW-Angebotes. Sofern Teile oder einzelne Formulierungen der Nutzungsbedingungen der geltenden Rechtslage nicht, nicht mehr oder nicht vollständig entsprechen sollten, bleiben die übrigen Teile der Nutzungsbedingungen in ihrem Inhalt und ihrer Gültigkeit davon unberührt.</p>
    <h2>Informationspflicht nach § 36 VSBG</h2>
    <p>Die Steuerberaterkanzlei Scheuer &amp; Partner mbB ist grundsätzlich nicht bereit und verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>"""
    legal("impressum.html", "Impressum und Haftung", inner)


def datenschutz():
    raw = (ROOT / "tools/source/datenschutz-original.txt").read_text(encoding="utf-8")
    raw = raw.split("Zusatzinformationen")[0]
    raw = raw.split("# \n", 1)[1] if "# \n" in raw else raw
    out, in_list = [], False
    para = []

    def flush():
        nonlocal para
        if para:
            out.append("<p>" + e(" ".join(para)) + "</p>")
            para = []
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            flush()
            continue
        if s.startswith("### "):
            flush(); out.append(f"<h3>{e(s[4:].strip())}</h3>")
        elif s.startswith("## "):
            flush(); out.append(f"<h2>{e(s[3:].strip())}</h2>")
        elif s.startswith("- "):
            flush()
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{e(s[2:].strip())}</li>")
            continue
        else:
            if in_list:
                out.append("</ul>"); in_list = False
            para.append(s)
            continue
        if in_list and not s.startswith("- "):
            pass
    flush()
    if in_list:
        out.append("</ul>")
    body = "\n    ".join(out)
    # Überschriften ohne Text (nur "## ") entfernen
    body = re.sub(r"<h[23]></h[23]>", "", body)
    inner = (f'\n    <p><span class="todo">Vor dem Livegang prüfen lassen. Dieser Text stammt unverändert von der bisherigen Seite. Auf der neuen Seite entfallen Matomo, YouTube, Formulare und Erinnerungsservice, solange sie nicht eingebunden werden. Die Kanzlei oder ihr Datenschutzbeauftragter passt den Text an.</span></p>\n    {body}\n'
             "    <h2>Diese Webseite</h2>\n    <p>Die Schriften und Skripte dieser Seite liegen auf demselben Server. Beim bloßen Aufruf gehen keine Anfragen an Dritte. Verlinkte externe Angebote (zum Beispiel das Online-Portal, Rechner und Karten) öffnen sich erst nach einem Klick in einem neuen Tab.</p>")
    legal("datenschutz.html", "Datenschutzerklärung", inner)


def sitemap():
    items = [("Startseite", "index.html", [])] + [
        ("Über uns", "ueber-uns.html", [("Team", "team.html"), ("Adresse · Anfahrt · Öffnungszeiten", "kontakt.html")]),
        ("Service & Leistungen", "steuerberatung.html", [("Steuerberatung", "steuerberatung.html"), ("Finanzbuchhaltung", "finanzbuchhaltung.html"), ("Lohnbuchhaltung", "lohnbuchhaltung.html"),
                                                         ("Nachfolgeberatung", "nachfolgeberatung.html"), ("Online-Tools, Downloads, Links, Videos", "service.html")]),
        ("Digitale Kanzlei", "digitale-kanzlei.html", []),
        ("Karriere", "karriere.html", [("Warum zu uns?", "karriere.html#warum"), ("Benefits", "karriere.html#benefits"), ("Offene Stellen", "karriere.html#stellen"), ("Blitzbewerbung", "karriere.html#bewerbung")]),
        ("News", "news.html", [("Steuernews für Mandanten", "news.html#mandanten"), ("Steuernews für Ärzte", "news.html#aerzte"), ("Steuernews-TV", "news.html#tv"), ("Newsletter", "news.html#newsletter")]),
        ("Impressum und Haftung", "impressum.html", []), ("Datenschutzerklärung", "datenschutz.html", [])]
    lis = "".join(f'<li><a href="{h}">{e(t)}</a>' + (("<ul>" + "".join(f'<li><a href="{sh}">{e(st)}</a></li>' for st, sh in subs) + "</ul>") if subs else "") + "</li>" for t, h, subs in items)
    legal("sitemap.html", "Sitemap", f'<ul class="sitemap">{lis}</ul>')


def not_found():
    p = head("Seite nicht gefunden", "Diese Seite gibt es nicht.", "404.html")
    p += f"""
  <section class="section" style="min-height:60vh;display:flex;flex-direction:column;justify-content:center;gap:1.4rem">
    <p class="kicker">Fehler 404</p>
    <h1 style="font-size:clamp(2.6rem,8vw,5.5rem);max-width:12ch">Diese Seite gibt es nicht.</h1>
    <p class="lead" style="margin:0">Vielleicht hilft Ihnen die Startseite oder die Sitemap weiter.</p>
    <p style="display:flex;flex-wrap:wrap;gap:.7rem"><a class="btn btn-lg" href="index.html">Zur Startseite</a><a class="btn btn-ghost btn-lg" href="sitemap.html">Sitemap</a></p>
  </section>"""
    p += foot()
    write("404.html", p)


if __name__ == "__main__":
    index()
    ueber_uns()
    team()
    kontakt()
    leistungen()
    digitale_kanzlei()
    service()
    karriere()
    news()
    impressum()
    datenschutz()
    sitemap()
    not_found()
