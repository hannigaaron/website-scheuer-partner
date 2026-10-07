#!/usr/bin/env python3
"""Zweite Runde: zehn Entwürfe rund um 05 (Siegel) und 08 (Bogenfenster).
Aufruf im Ordner design/:  python3 runde2.py
Erzeugt SVG (vier Fassungen), PNG (transparent), Übersichtsblätter und PDF in design/logos2/."""
import pathlib

from make_logos import Canvas, VARIANTS, bars, text_path, arch_open
import make_sheets

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "logos2"
(OUT / "svg").mkdir(parents=True, exist_ok=True)

NAME_FONT = "CormorantGaramond-normal"
ITAL_FONT = "CormorantGaramond-italic"


def block_d(s, x0=0.0, y0=0.0):
    """Block mit drei ausgeschnittenen Balken (Maßverhältnis von Entwurf 05)."""
    k = s / 112.0
    d = f"M{x0:g} {y0:g}H{x0 + s:g}V{y0 + s:g}H{x0:g}Z "
    x = 24 * k
    for w in (6 * k, 24 * k, 6 * k):
        d += f"M{x0 + x:.2f} {y0 + 16 * k:.2f}V{y0 + s - 16 * k:.2f}H{x0 + x + w:.2f}V{y0 + 16 * k:.2f}Z "
        x += w + 11 * k
    return d


def name_and_sub(c, tx, base, size=80, sub_size=19, gap=44, anchor="start"):
    """Schrift von Entwurf 01: Cormorant 600 und Inter-Zeile."""
    c.text("Scheuer & Partner", NAME_FONT, size, tx, base, wght=600, anchor=anchor, track=-0.005)
    c.text("Steuerberatungsgesellschaft mbB", "Inter-normal", sub_size, tx, base + gap, fill="{S}", wght=500,
           anchor=anchor, track=0.1)


# --- Siegel-Familie (Basis 05) ---------------------------------------------
def l11():
    c = Canvas()
    s = 124
    c.path(block_d(s), rule="evenodd", bbox=(0, 0, s, s))
    name_and_sub(c, s + 42, 66, size=80, gap=42)
    return c


def l12():
    c = Canvas()
    s = 100
    c.path(block_d(s, -s / 2, 0), rule="evenodd", bbox=(-s / 2, 0, s / 2, s))
    name_and_sub(c, 0, s + 84, size=84, gap=46, anchor="middle")
    return c


def l13():
    c = Canvas()
    w, h = 112, 152
    r = w / 2
    d = f"M0 {h}V{r}A{r} {r} 0 0 1 {w} {r}V{h}Z "
    x = (w - 54) / 2
    for bw in (5, 20, 5):
        d += f"M{x:g} {h - 22}V{h - 22 - 68}H{x + bw:g}V{h - 22}Z "
        x += bw + 12
    c.path(d, rule="evenodd", bbox=(0, 0, w, h))
    tx = w + 40
    c.text("Scheuer", NAME_FONT, 76, tx, 78, wght=600)
    c.text("& Partner", ITAL_FONT, 76, tx, 144, fill="{G}", wght=500)
    c.text("STEUERBERATUNGSGESELLSCHAFT MBB", "Inter-normal", 14.5, tx, 180, fill="{S}", wght=600, track=0.2)
    return c


def l14():
    c = Canvas()
    r = 66
    d = f"M{-r} 0A{r} {r} 0 1 0 {r} 0A{r} {r} 0 1 0 {-r} 0Z "
    x = -27
    for bw in (5, 20, 5):
        d += f"M{x:g} -34V34H{x + bw:g}V-34Z "
        x += bw + 12
    c.path(d, rule="evenodd", bbox=(-r, -r, r, r))
    tx = r + 40
    c.text("SCHEUER & PARTNER", "Marcellus-normal", 50, tx, -2, track=0.06)
    c.text("Steuerberatungsgesellschaft mbB", "Inter-normal", 19, tx, 36, fill="{S}", wght=500, track=0.06)
    return c


def l15():
    c = Canvas()
    s = 128
    size = 72
    font, wg = "Jost-normal", 500
    wS = text_path("S", font, size, wg)[1]
    wP = text_path("P", font, size, wg)[1]
    bar_w, sp = 4, 17
    total = wS + sp + bar_w + sp + wP
    x = (s - total) / 2
    base = s / 2 + size * 0.35
    dS, _ = text_path("S", font, size, wg, ox=x, oy=base)
    dP, _ = text_path("P", font, size, wg, ox=x + wS + sp + bar_w + sp, oy=base)
    bx = x + wS + sp
    cap = size * 0.70
    ext = 13   # der Balken ragt über die Buchstaben hinaus, so liest er sich nicht als I
    bar = f"M{bx:.2f} {base - cap - ext:.2f}H{bx + bar_w:.2f}V{base + ext:.2f}H{bx:.2f}Z"
    c.path(f"M0 0H{s}V{s}H0Z {dS} {dP} {bar}", rule="evenodd", bbox=(0, 0, s, s))
    tx = s + 40
    c.text("SCHEUER & PARTNER", "Jost-normal", 46, tx, 62, wght=500, track=0.12)
    c.text("Steuerberatungsgesellschaft mbB", "Inter-normal", 19, tx, 100, fill="{S}", wght=500, track=0.06)
    return c


# --- Bogenfenster-Familie (Basis 08) ----------------------------------------
def ring(w, h, t, inset=0.0, closed=False):
    """Bogenlinie (Ring). inset verschiebt nach innen, closed schließt die Unterkante."""
    xo0, xo1 = inset, w - inset
    ro = (xo1 - xo0) / 2
    yb = h - inset if closed else h
    outer = f"M{xo0:g} {yb:g}V{ro + inset:g}A{ro:g} {ro:g} 0 0 1 {xo1:g} {ro + inset:g}V{yb:g}Z"
    xi0, xi1 = xo0 + t, xo1 - t
    ri = (xi1 - xi0) / 2
    yi = yb - t if closed else yb
    inner = f"M{xi0:g} {yi:g}V{ri + inset + t:g}A{ri:g} {ri:g} 0 0 1 {xi1:g} {ri + inset + t:g}V{yi:g}Z"
    return outer + " " + inner


def l16():
    c = Canvas()
    w, h = 108, 150
    c.path(ring(w, h, 5, 0, closed=True), rule="evenodd", bbox=(0, 0, w, h))
    bars(c, w / 2 - 22.5, 54, 76, widths=(4, 15, 4), gap=10)
    c.rect(-10, h + 9, w + 20, 4, "{G}")
    tx = w + 44
    c.text("Scheuer", NAME_FONT, 76, tx, 78, wght=600)
    c.text("& Partner", ITAL_FONT, 76, tx, 144, fill="{G}", wght=500)
    c.text("STEUERBERATUNGSGESELLSCHAFT MBB", "Inter-normal", 14.5, tx, 180, fill="{S}", wght=600, track=0.2)
    return c


def l17():
    c = Canvas()
    w, h = 116, 150
    c.path(ring(w, h, 4.5, 0) + " " + ring(w, h, 2.5, 13), rule="evenodd", bbox=(0, 0, w, h))
    bars(c, w / 2 - 22.5, 70, 58, widths=(4, 15, 4), gap=10)
    tx = w + 40
    c.text("Scheuer", NAME_FONT, 76, tx, 78, wght=600)
    c.text("& Partner", ITAL_FONT, 76, tx, 144, fill="{G}", wght=500)
    c.text("STEUERBERATUNGSGESELLSCHAFT MBB", "Inter-normal", 14.5, tx, 180, fill="{S}", wght=600, track=0.2)
    return c


def l18():
    c = Canvas()
    w, h = 96, 132
    c.path(ring(w, h, 5, 0).replace("M", "M", 1), rule="evenodd", bbox=(-w / 2, 0, w / 2, h))
    # Bogen um die Mitte setzen
    c.items[-1] = c.items[-1].replace("<path ", f'<path transform="translate({-w / 2:g} 0)" ', 1)
    bars(c, -20, 50, 66, widths=(4, 14, 4), gap=9)
    base = h + 78
    wn = text_path("Scheuer", NAME_FONT, 76, 600, -0.004)[1]
    wa = text_path("&", ITAL_FONT, 76, 500)[1]
    wp = text_path("Partner", NAME_FONT, 76, 600, -0.004)[1]
    gap = 18
    total = wn + gap + wa + gap + wp
    x = -total / 2
    c.text("Scheuer", NAME_FONT, 76, x, base, wght=600, track=-0.004)
    c.text("&", ITAL_FONT, 76, x + wn + gap, base, fill="{G}", wght=500)
    c.text("Partner", NAME_FONT, 76, x + wn + gap + wa + gap, base, wght=600, track=-0.004)
    c.text("STEUERBERATUNGSGESELLSCHAFT MBB", "Inter-normal", 15, 0, base + 42, fill="{S}", wght=600, track=0.22,
           anchor="middle")
    return c


def l19():
    c = Canvas()
    gap = 12
    specs = [(22, 112), (50, 140), (22, 112)]
    x, base = 0.0, 140.0
    d = ""
    for w, h in specs:
        r = w / 2
        d += f"M{x:g} {base:g}V{base - h + r:g}A{r:g} {r:g} 0 0 1 {x + w:g} {base - h + r:g}V{base:g}Z "
        x += w + gap
    c.path(d, bbox=(0, 0, x - gap, base))
    tx = x - gap + 42
    c.text("Scheuer & Partner", NAME_FONT, 78, tx, 82, wght=600, track=-0.004)
    c.text("Steuerberatungsgesellschaft mbB", "Inter-normal", 19, tx, 126, fill="{S}", wght=500, track=0.1)
    return c


def l20():
    c = Canvas()
    w, h = 136, 160
    c.path(ring(w, h, 5, 0), rule="evenodd", bbox=(0, 0, w, h))
    size = 112
    wa = text_path("&", ITAL_FONT, size, 500)[1]
    c.text("&", ITAL_FONT, size, w / 2 - wa / 2 + 3, h - 30, fill="{G}", wght=500)
    tx = w + 42
    c.text("Scheuer", NAME_FONT, 76, tx, 88, wght=600)
    c.text("Partner", NAME_FONT, 76, tx, 154, wght=600)
    c.text("STEUERBERATUNGSGESELLSCHAFT MBB", "Inter-normal", 14.5, tx, 190, fill="{S}", wght=600, track=0.2)
    return c


LOGOS2 = [
    ("11", "siegel-serife", "Siegel mit Serife", l11,
     "Zeichen von 05, Schrift von 01. Der Block trägt, die Serife macht ihn ruhiger. Das ist dein Wunsch."),
    ("12", "siegel-gestapelt", "Siegel gestapelt", l12,
     "Dasselbe Paar übereinander und mittig. Passt auf Briefbogen und Visitenkarte."),
    ("13", "siegel-bogen", "Siegel im Bogen", l13,
     "05 trifft 08. Der grüne Block bekommt oben den Bogen der Website."),
    ("14", "plakette", "Plakette", l14,
     "Der Block als Scheibe mit drei ausgeschnittenen Balken, dazu Schrift in Großbuchstaben."),
    ("15", "siegel-sp", "Siegel mit S | P", l15,
     "Initialen im Block ausgeschnitten, der Balken trennt sie. Stark als Profilbild."),
    ("16", "bogen-sockel", "Bogen mit Sockel", l16,
     "Der Bogen von 08 ganz geschlossen, mit Fensterbank. Wirkt wie ein Portal."),
    ("17", "bogen-doppelt", "Bogen doppelt", l17,
     "Zwei Linien statt einer. Wirkt wertiger, ist bei kleiner Größe aber schwerer zu lesen."),
    ("18", "bogen-gestapelt", "Bogen gestapelt", l18,
     "08 mittig, die Schrift darunter in einer Zeile. Gut für den Briefkopf."),
    ("19", "dreifach-bogen", "Dreifach-Bogen", l19,
     "Aus den drei Balken werden drei Bögen. Das eigenständigste Zeichen dieser Runde."),
    ("20", "bogen-et", "Bogen mit Et-Zeichen", l20,
     "Das Et-Zeichen als Bildzeichen im Bogen. Verspielter, passt zur Wortmarke 04."),
]


def main():
    for num, key, name, fn, _ in LOGOS2:
        base = fn().svg()
        for vname, cols in VARIANTS.items():
            s = base
            for k, v in cols.items():
                s = s.replace("{" + k + "}", v)
            (OUT / "svg" / f"{num}-{key}-{vname}.svg").write_text(s, encoding="utf-8")
        print(num, name, "ok")
    make_sheets.build(LOGOS2, OUT / "svg", OUT, prefix="uebersicht2", subtitle="Logo-Entwürfe, zweite Runde")


if __name__ == "__main__":
    main()
