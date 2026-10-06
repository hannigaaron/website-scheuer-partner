#!/usr/bin/env python3
"""Packt die ganze Seite in EINE HTML-Datei: Scheuer-Partner-Entwurf.html

Enthalten sind alle Seiten, das Stylesheet, die Schriften, die Bilder und die
Skripte. Die Datei läuft per Doppelklick ohne Internet. Ein Klick auf einen
Menüpunkt wechselt die Seite (Adresse #/team, #/steuerberatung usw.).

Aufruf im Repo-Ordner (nach tools/build.py):  python3 tools/bundle.py
"""
import base64
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "Scheuer-Partner-Entwurf.html"
SLUGS = ["index", "ueber-uns", "team", "kontakt", "steuerberatung", "finanzbuchhaltung", "lohnbuchhaltung",
         "nachfolgeberatung", "digitale-kanzlei", "service", "karriere", "news", "impressum", "datenschutz", "sitemap"]
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".woff2": "font/woff2"}


def data_uri(path):
    p = ROOT / path
    return f"data:{MIME[p.suffix]};base64," + base64.b64encode(p.read_bytes()).decode()


def rewrite_links(html):
    def sub(m):
        slug, anchor = m.group(1), m.group(3)
        if slug not in SLUGS:
            return m.group(0)
        return f'href="#/{slug}/{anchor}"' if anchor else f'href="#/{slug}"'
    return re.sub(r'href="([a-z0-9-]+)\.html(#([a-z0-9-]+))?"', sub, html)


def grab(pattern, text):
    m = re.search(pattern, text, re.S)
    if not m:
        raise SystemExit("Muster nicht gefunden: " + pattern)
    return m.group(0)


pages = {}
for slug in SLUGS:
    src = (ROOT / f"{slug}.html").read_text(encoding="utf-8")
    title = re.search(r"<title>(.*?)</title>", src, re.S).group(1)
    pages[slug] = {
        "title": re.sub(r"&amp;", "&", title),
        "header": rewrite_links(grab(r'<header class="nav".*?</header>', src)),
        "main": rewrite_links(grab(r'<main id="main">.*?</main>', src)),
    }
index_src = (ROOT / "index.html").read_text(encoding="utf-8")
pages["_footer"] = rewrite_links(grab(r'<footer class="footer">.*?</footer>', index_src))

# Bilder einmal einbetten, die Seiten verweisen darauf
assets = {}
used = set()
blob = json.dumps(pages)
used.update(re.findall(r'img/[A-Za-z0-9_.-]+', blob))
used.add("img/logo.png")
for k in sorted(used):
    assets[k] = data_uri(k)

# Schriften in die CSS einbetten
fonts_css = (ROOT / "fonts/fonts.css").read_text(encoding="utf-8")
fonts_css = re.sub(r"url\(([^)]+\.woff2)\)", lambda m: f"url({data_uri('fonts/' + m.group(1))})", fonts_css)
css = (ROOT / "styles.css").read_text(encoding="utf-8")
extra = "@keyframes pagein{from{opacity:0}to{opacity:1}}body{animation:pagein .5s ease both}"

script = (ROOT / "script.js").read_text(encoding="utf-8")
# Das Logo im Einstieg kommt aus dem eingebetteten Vorrat
script = script.replace('src="img/logo.png"', 'src="\' + window.__ASSETS[\'img/logo.png\'] + \'"')
vendor = "\n".join((ROOT / f"vendor/{n}").read_text(encoding="utf-8") for n in ("gsap.min.js", "ScrollTrigger.min.js", "lenis.min.js"))


def safe_json(obj):
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


BOOT = """(function(){
  var A=JSON.parse(document.getElementById('assets').textContent);
  var P=JSON.parse(document.getElementById('pages').textContent);
  window.__ASSETS=A;
  var m=(location.hash||'').match(/^#\\/([a-z0-9-]+)(?:\\/([a-z0-9-]+))?/);
  var slug=(m&&P[m[1]]&&m[1]!=='_footer')?m[1]:'index', anchor=m&&m[2];
  var pg=P[slug];
  function img(s){return s.replace(/src="(img\\/[^"]+)"/g,function(_,k){return 'src="'+A[k]+'"'})}
  document.title=pg.title;
  document.body.insertAdjacentHTML('afterbegin',
    '<a class="skip" href="#main">Zum Inhalt springen</a><div class="progress" id="progress" aria-hidden="true"></div>'+
    img(pg.header)+img(pg.main)+img(P._footer));
  /* Seitenwechsel: neue Adresse mit #/ lädt die Seite neu, dadurch starten alle Animationen sauber */
  addEventListener('hashchange',function(){ if(/^#\\//.test(location.hash)) location.reload(); });
  if(anchor) addEventListener('load',function(){ setTimeout(function(){ var t=document.getElementById(anchor); if(t) t.scrollIntoView(); },900); });
})();"""

html = f"""<!DOCTYPE html>
<html lang="de" class="no-js">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>Scheuer &amp; Partner mbB Steuerberatungsgesellschaft</title>
<meta name="robots" content="noindex, nofollow" />
<meta name="theme-color" content="#ffffff" />
<link rel="icon" href="{data_uri('favicon.png')}" type="image/png" />
<style>
{fonts_css}
{css}
{extra}
</style>
</head>
<body>
<script id="assets" type="application/json">{safe_json(assets)}</script>
<script id="pages" type="application/json">{safe_json(pages)}</script>
<script>{BOOT}</script>
<script>{vendor}</script>
<script>{script}</script>
</body>
</html>
"""
OUT.write_text(html, encoding="utf-8")
print("geschrieben", OUT.name, round(OUT.stat().st_size / 1024), "KB")
