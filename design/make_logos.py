#!/usr/bin/env python3
"""Erzeugt zehn Logo-Entwürfe für Scheuer & Partner als echte Vektordateien.

Die Schrift wird in Pfade umgewandelt (kein Font nötig). Jedes Logo gibt es in
vier Fassungen: Farbe, Negativ (für dunklen Grund), Schwarz und Weiß.
Aufruf im Ordner design/:  python3 make_logos.py
"""
import io
import pathlib

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = pathlib.Path(__file__).resolve().parent
FONTS = HERE / "fonts"
OUT = HERE / "logos"
(OUT / "svg").mkdir(parents=True, exist_ok=True)

VARIANTS = {
    "farbe":   {"G": "#16A355", "T": "#2B2B2B", "S": "#5B5B5B"},
    "negativ": {"G": "#16A355", "T": "#FFFFFF", "S": "#C4C4C4"},
    "schwarz": {"G": "#000000", "T": "#000000", "S": "#000000"},
    "weiss":   {"G": "#FFFFFF", "T": "#FFFFFF", "S": "#FFFFFF"},
}

_cache = {}


def load(name, wght=None):
    key = (name, wght)
    if key in _cache:
        return _cache[key]
    tt = TTFont(FONTS / f"{name}.woff2")
    if "fvar" in tt and wght:
        tt = instancer.instantiateVariableFont(tt, {"wght": wght})
    buf = io.BytesIO()
    tt.flavor = None
    tt.save(buf)
    data = buf.getvalue()
    tt2 = TTFont(io.BytesIO(data))
    hbfont = hb.Font(hb.Face(hb.Blob(data)))
    _cache[key] = (tt2, hbfont, tt2["head"].unitsPerEm)
    return _cache[key]


def text_path(text, font, size, wght=None, track=0.0, features=None):
    """Gibt (Pfad ab Nullpunkt auf der Grundlinie, Breite) zurück. track in em."""
    tt, hbf, upem = load(font, wght)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbf, buf, features or {"kern": True, "liga": True})
    gs = tt.getGlyphSet()
    s = size / upem
    x = 0.0
    parts = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        gname = tt.getGlyphName(info.codepoint)
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
        gs[gname].draw(TransformPen(pen, (s, 0, 0, -s, x + pos.x_offset * s, -pos.y_offset * s)))
        parts.append(pen.getCommands())
        x += pos.x_advance * s + track * size
    return " ".join(p for p in parts if p), x - track * size


class Canvas:
    """Sammelt Formen und Text, merkt sich den belegten Bereich."""

    def __init__(self):
        self.items = []
        self.x0 = self.y0 = 1e9
        self.x1 = self.y1 = -1e9

    def _grow(self, x0, y0, x1, y1):
        self.x0, self.y0 = min(self.x0, x0), min(self.y0, y0)
        self.x1, self.y1 = max(self.x1, x1), max(self.y1, y1)

    def rect(self, x, y, w, h, fill="{G}"):
        self.items.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}"/>')
        self._grow(x, y, x + w, y + h)

    def path(self, d, fill="{G}", bbox=None, rule="nonzero", stroke=None, sw=0):
        st = f' stroke="{stroke}" stroke-width="{sw:g}"' if stroke else ""
        fl = f'fill="{fill}"' if fill else 'fill="none"'
        self.items.append(f'<path d="{d}" {fl} fill-rule="{rule}"{st}/>')
        if bbox:
            self._grow(*bbox)

    def text(self, txt, font, size, x, y, fill="{T}", wght=None, track=0.0, anchor="start"):
        d, w = text_path(txt, font, size, wght, track)
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        self.items.append(f'<path transform="translate({x:.2f} {y:.2f})" d="{d}" fill="{fill}"/>')
        self._grow(x, y - size * 0.74, x + w, y + size * 0.22)
        return w

    def svg(self, pad=34):
        x0, y0, x1, y1 = self.x0 - pad, self.y0 - pad, self.x1 + pad, self.y1 + pad
        w, h = x1 - x0, y1 - y0
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}" '
                f'width="{w:.0f}" height="{h:.0f}">' + "".join(self.items) + "</svg>")


def bars(c, x, y, h, widths=(5, 22, 5), gap=14, fill="{G}"):
    """Die drei Balken des bisherigen Logos. x = linke Kante."""
    cx = x
    for w in widths:
        c.rect(cx, y, w, h, fill)
        cx += w + gap
    return cx - gap - x


def arch_open(x, yb, w, h):
    """Bogenöffnung (Rechteck mit Halbkreis oben) als Pfad, Unterkante yb."""
    r = w / 2
    return f"M{x:g} {yb:g}V{yb - h + r:g}A{r:g} {r:g} 0 0 1 {x + w:g} {yb - h + r:g}V{yb:g}Z"


# ---------------------------------------------------------------------------
# Zehn Entwürfe
# ---------------------------------------------------------------------------
def l01_pfeiler():
    c = Canvas()
    bars(c, -30, 0, 92)
    c.rect(-84, 104, 168, 3)
    c.text("Scheuer & Partner", "CormorantGaramond-normal", 84, 0, 200, wght=600, anchor="middle", track=-0.005)
    c.text("Steuerberatungsgesellschaft mbB", "Inter-normal", 19, 0, 246, fill="{S}", wght=500, anchor="middle", track=0.1)
    return c


def l02_viadukt():
    c = Canvas()
    # Deck oben, darunter Pfeiler und offene Bögen wie am Enzviadukt
    bw, bh = 156, 100
    ow, oh, gap = 24, 76, 13
    n = 4
    x0 = (bw - (n * ow + (n - 1) * gap)) / 2
    xs = [x0 + i * (ow + gap) for i in range(n)]
    r = ow / 2
    yt = bh - oh
    d = f"M0 0H{bw}V{bh}"
    for x in reversed(xs):
        d += f"H{x + ow:g}V{yt + r:g}A{r:g} {r:g} 0 0 0 {x:g} {yt + r:g}V{bh}"
    d += "H0Z"
    c.path(d, bbox=(0, 0, bw, bh))
    tx = bw + 34
    c.text("SCHEUER & PARTNER", "Marcellus-normal", 50, tx, 56, track=0.06)
    c.text("Steuerberatungsgesellschaft mbB", "Inter-normal", 19, tx, 94, fill="{S}", wght=500, track=0.06)
    return c


def l03_monogramm():
    c = Canvas()
    s = 144
    c.path(f"M0 0H{s}V{s}H0Z M5 5V{s - 5}H{s - 5}V5Z", rule="evenodd", fill="{T}", bbox=(0, 0, s, s))
    size, gap = 44, 7
    wS = text_path("S", "CormorantGaramond-normal", size, 600)[1]
    wA = text_path("&", "CormorantGaramond-italic", size + 8, 500)[1]
    wP = text_path("P", "CormorantGaramond-normal", size, 600)[1]
    total = wS + gap + wA + gap + wP
    x = (s - total) / 2
    base = s / 2 + size * 0.33
    c.text("S", "CormorantGaramond-normal", size, x, base, wght=600)
    c.text("&", "CormorantGaramond-italic", size + 8, x + wS + gap, base, fill="{G}", wght=500)
    c.text("P", "CormorantGaramond-normal", size, x + wS + gap + wA + gap, base, wght=600)
    tx = s + 36
    c.text("Scheuer", "CormorantGaramond-normal", 62, tx, 60, wght=600)
    c.text("& Partner", "CormorantGaramond-italic", 62, tx, 122, fill="{G}", wght=500)
    c.text("STEUERBERATUNGSGESELLSCHAFT MBB", "Inter-normal", 14.5, tx, 156, fill="{S}", wght=600, track=0.2)
    return c


def l04_wortmarke():
    c = Canvas()
    w1 = c.text("Scheuer", "PlayfairDisplay-normal", 92, 0, 0, wght=600, track=-0.01)
    w2 = c.text("&", "PlayfairDisplay-italic", 92, w1 + 22, 0, fill="{G}", wght=500)
    c.text("Partner", "PlayfairDisplay-normal", 92, w1 + 22 + w2 + 22, 0, wght=600, track=-0.01)
    c.rect(0, 30, 70, 3)
    c.text("STEUERBERATUNGSGESELLSCHAFT MBB", "Inter-normal", 17, 0, 74, fill="{S}", wght=600, track=0.26)
    return c


def l05_siegel():
    c = Canvas()
    s = 112
    d = f"M0 0H{s}V{s}H0Z "
    x = 24
    for w in (6, 24, 6):
        d += f"M{x:g} 16V{s - 16}H{x + w:g}V16Z "
        x += w + 11
    c.path(d, rule="evenodd", bbox=(0, 0, s, s))
    tx = s + 34
    c.text("SCHEUER", "Jost-normal", 54, tx, 50, wght=500, track=0.14)
    c.text("& PARTNER", "Jost-normal", 54, tx, 104, wght=500, track=0.14, fill="{G}")
    return c


def l06_aufstieg():
    c = Canvas()
    h = [44, 70, 98]
    x = 0
    for hh in h:
        c.rect(x, 98 - hh, 20, hh)
        x += 31
    tx = x - 11 + 38
    c.text("Scheuer & Partner", "Inter-normal", 60, tx, 62, wght=600, track=-0.025)
    c.text("Steuerberatungsgesellschaft mbB", "Inter-normal", 20, tx, 98, fill="{S}", wght=500, track=0.04)
    return c


def l07_kreis():
    c = Canvas()
    r = 72
    d = (f"M{-r} 0A{r} {r} 0 1 0 {r} 0A{r} {r} 0 1 0 {-r} 0Z "
         f"M{-r + 5} 0A{r - 5} {r - 5} 0 1 1 {r - 5} 0A{r - 5} {r - 5} 0 1 1 {-r + 5} 0Z")
    c.path(d, rule="evenodd", bbox=(-r, -r, r, r))
    bars(c, -28, -33, 66, widths=(4, 20, 4), gap=13)
    c.text("SCHEUER & PARTNER", "Jost-normal", 36, 0, r + 62, wght=500, track=0.2, anchor="middle")
    c.text("STEUERBERATUNGSGESELLSCHAFT MBB", "Inter-normal", 12.5, 0, r + 90, fill="{S}", wght=600, track=0.22, anchor="middle")
    return c


def l08_bogen():
    c = Canvas()
    w, h = 108, 150
    r = w / 2
    outer = f"M0 {h}V{r}A{r} {r} 0 0 1 {w} {r}V{h}Z"
    t = 5
    inner = f"M{t} {h}V{r}A{r - t} {r - t} 0 0 1 {w - t} {r}V{h}Z"
    c.path(outer + " " + inner, rule="evenodd", bbox=(0, 0, w, h))
    bars(c, w / 2 - 22.5, 58, 70, widths=(4, 15, 4), gap=10)
    tx = w + 38
    c.text("Scheuer", "CormorantGaramond-normal", 76, tx, 76, wght=600)
    c.text("& Partner", "CormorantGaramond-italic", 76, tx, 142, fill="{G}", wght=500)
    c.text("STEUERBERATUNGSGESELLSCHAFT MBB", "Inter-normal", 14.5, tx, 178, fill="{S}", wght=600, track=0.2)
    return c


def l09_initialen():
    c = Canvas()
    w1 = c.text("S", "Jost-normal", 150, 0, 0, wght=500)
    c.rect(w1 + 20, -104, 8, 104)
    c.text("P", "Jost-normal", 150, w1 + 48, 0, wght=500)
    total = w1 + 48 + text_path("P", "Jost-normal", 150, 500)[1]
    c.text("SCHEUER & PARTNER", "Inter-normal", 21, total / 2, 52, wght=600, track=0.3, anchor="middle")
    return c


def l10_waage():
    c = Canvas()
    bw = 116                                   # Breite des Balkens
    mid = bw / 2
    c.rect(0, 0, bw, 4)                        # Waagbalken
    c.rect(mid - 4, 4, 8, 82)                  # Säule
    c.rect(mid - 26, 86, 52, 5)                # Fuß
    c.path(f"M{mid:g} -8m-5 0a5 5 0 1 0 10 0a5 5 0 1 0 -10 0Z", bbox=(mid - 5, -13, mid + 5, 2))  # Knauf
    for cx in (12, bw - 12):                   # zwei Schalen mit je zwei Hängern
        c.path(f"M{cx - 20:g} 62A20 20 0 0 0 {cx + 20:g} 62Z", bbox=(cx - 20, 62, cx + 20, 82))
        c.path(f"M{cx:g} 4L{cx - 20:g} 62M{cx:g} 4L{cx + 20:g} 62", fill=None, stroke="{G}", sw=2.2,
               bbox=(cx - 20, 4, cx + 20, 62))
    tx = bw + 44
    c.text("Scheuer & Partner", "CormorantGaramond-normal", 70, tx, 56, wght=600, track=-0.004)
    c.text("Steuerberatungsgesellschaft mbB", "Inter-normal", 19, tx, 94, fill="{S}", wght=500, track=0.08)
    return c


LOGOS = [
    ("01", "pfeiler", "Pfeiler", l01_pfeiler,
     "Weiterentwicklung des heutigen Zeichens: drei Pfeiler auf einem Sockel. Bewahrt die Identität und wirkt ruhiger."),
    ("02", "viadukt", "Viadukt", l02_viadukt,
     "Reihe von Bögen nach dem Enzviadukt in Bietigheim. Regional und beständig, in Großbuchstaben."),
    ("03", "monogramm", "Monogramm", l03_monogramm,
     "S und P mit grünem Et-Zeichen im Rahmen. Funktioniert klein, etwa als Profilbild."),
    ("04", "wortmarke", "Wortmarke", l04_wortmarke,
     "Nur Schrift. Kontrastreiche Serife mit grünem Et-Zeichen. Klassisch und edel."),
    ("05", "siegel", "Siegel", l05_siegel,
     "Grüner Block mit drei ausgeschnittenen Balken. Klar, modern, gut auf jedem Grund."),
    ("06", "aufstieg", "Aufstieg", l06_aufstieg,
     "Drei Balken wachsen nach oben. Steht für Zahlen und Entwicklung, ohne Pfeil-Klischee."),
    ("07", "kreis", "Kreis", l07_kreis,
     "Drei Balken im Ring. Wirkt wie ein Stempel oder Siegel und passt auf Briefbogen."),
    ("08", "bogen", "Bogenfenster", l08_bogen,
     "Der Bogen aus der Website mit den drei Balken darin. Verbindet Logo und Webauftritt."),
    ("09", "initialen", "Initialen", l09_initialen,
     "S | P. Der Balken ersetzt das Et-Zeichen. Kurz und stark, gut für Social Media."),
    ("10", "waage", "Waage", l10_waage,
     "Balken, Pfeiler und zwei Schalen deuten die Waage an. Steht für Ausgleich und Recht."),
]


def main():
    for num, key, name, fn, _ in LOGOS:
        base = fn().svg()
        for vname, cols in VARIANTS.items():
            s = base
            for k, v in cols.items():
                s = s.replace("{" + k + "}", v)
            (OUT / "svg" / f"{num}-{key}-{vname}.svg").write_text(s, encoding="utf-8")
        print(num, name, "ok")


if __name__ == "__main__":
    main()
