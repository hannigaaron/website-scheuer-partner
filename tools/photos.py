#!/usr/bin/env python3
"""Bereitet die Fotos auf: zuschneiden, verkleinern, leicht nachschärfen.
Die Farben bleiben unverändert, es liegt kein Filter über den Bildern.
Außerdem: Bildmarke, Favicon und Vorschaubild aus dem Logo.
Aufruf im Repo-Ordner:  python3 tools/photos.py
"""
import pathlib
import numpy as np
from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "tools/source/photos"
OUT = ROOT / "img"


def save(im, name, q=82):
    im = im.convert("RGB").filter(ImageFilter.UnsharpMask(1.0, 40, 2))
    im.save(OUT / name, "JPEG", quality=q, optimize=True, progressive=True)
    print(name, im.size, (OUT / name).stat().st_size // 1024, "KB")


def wide(src, w=1600):
    im = Image.open(SRC / src)
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


save(wide("src-start.jpg"), "hero.jpg", 84)
save(wide("src-ueber.jpg"), "kopf-ueber-uns.jpg", 80)
save(wide("src-leistungen.jpg"), "kopf-leistungen.jpg", 82)
save(wide("src-karriere.jpg"), "kopf-karriere.jpg", 80)
save(wide("src-news.jpg"), "kopf-news.jpg", 82)
save(wide("src-digital.jpg"), "kopf-digital.jpg", 80)

t = Image.open(SRC / "src-leistungen.jpg").crop((560, 0, 1919, 1132))
save(t.resize((1100, round(1132 * 1100 / 1359)), Image.LANCZOS), "digital-teaser.jpg", 82)
save(Image.open(SRC / "src-karriere.jpg").crop((560, 150, 1260, 1150)), "karriere-teaser.jpg", 84)

# Favicon und Vorschaubild auf Weiß
lg = Image.open(OUT / "logo.png").convert("RGBA")
mark = Image.open(OUT / "logo-mark.png").convert("RGBA")
side = max(mark.size) + 44
fav = Image.new("RGBA", (side, side), (255, 255, 255, 255))
fav.alpha_composite(mark, ((side - mark.width) // 2, (side - mark.height) // 2))
fav.resize((256, 256), Image.LANCZOS).convert("RGB").save(ROOT / "favicon.png")
og = Image.new("RGBA", (1200, 630), (255, 255, 255, 255))
l = lg.copy(); l.thumbnail((820, 420))
og.alpha_composite(l, ((1200 - l.width) // 2, (630 - l.height) // 2))
og.convert("RGB").save(ROOT / "og-image.jpg", quality=88)
