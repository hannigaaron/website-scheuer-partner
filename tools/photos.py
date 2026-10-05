#!/usr/bin/env python3
"""Bereitet die Fotos auf: Graustufen, dann Verlauf von Tannengrün nach Elfenbein.
Dadurch verschwindet das Blau der Stockfotos, alle Bilder wirken einheitlich.
Aufruf im Repo-Ordner:  python3 tools/photos.py
"""
import pathlib
import numpy as np
from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "tools/source/photos"
OUT = ROOT / "img"

STOPS = [(0.00, (7, 28, 19)), (0.45, (52, 92, 72)), (0.78, (170, 192, 176)), (1.00, (246, 243, 234))]


def duotone(im, contrast=1.12, lift=0.0):
    g = np.asarray(im.convert("L")).astype(np.float32) / 255.0
    g = np.clip((g - 0.5) * contrast + 0.5 + lift, 0, 1)
    xs = [s[0] for s in STOPS]
    out = np.stack([np.interp(g, xs, [s[1][c] for s in STOPS]) for c in range(3)], axis=-1)
    return Image.fromarray(out.astype(np.uint8))


def save(im, name, q=80):
    im.save(OUT / name, "JPEG", quality=q, optimize=True, progressive=True)
    print(name, im.size, (OUT / name).stat().st_size // 1024, "KB")


def wide(src, w=1600):
    im = Image.open(SRC / src)
    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    return duotone(im).filter(ImageFilter.UnsharpMask(1.0, 40, 2))


save(wide("src-start.jpg"), "hero.jpg", 82)
save(wide("src-ueber.jpg"), "kopf-ueber-uns.jpg", 78)
save(wide("src-leistungen.jpg"), "kopf-leistungen.jpg", 80)
save(wide("src-karriere.jpg"), "kopf-karriere.jpg", 78)
save(wide("src-news.jpg"), "kopf-news.jpg", 80)
save(wide("src-digital.jpg"), "kopf-digital.jpg", 78)

t = Image.open(SRC / "src-leistungen.jpg").crop((560, 0, 1919, 1132))
t = t.resize((1100, round(1132 * 1100 / 1359)), Image.LANCZOS)
save(duotone(t).filter(ImageFilter.UnsharpMask(1.0, 40, 2)), "digital-teaser.jpg", 80)
k = Image.open(SRC / "src-karriere.jpg").crop((560, 150, 1260, 1150))
save(duotone(k).filter(ImageFilter.UnsharpMask(1.0, 40, 2)), "karriere-teaser.jpg", 82)
v = Image.open(SRC / "src-start.jpg").crop((120, 120, 1120, 809))
save(duotone(v).filter(ImageFilter.UnsharpMask(1.0, 40, 2)), "viadukt-teaser.jpg", 82)

# Logo für dunkle Flächen: Schrift elfenbein, Balken bleiben grün
lg = Image.open(OUT / "logo.png").convert("RGBA")
a = np.asarray(lg).copy()
rows = a[..., 3].max(axis=1)
ys = np.where(rows > 8)[0]
gap = next(i for i in range(ys[0], ys[-1]) if rows[i] <= 8)
a[gap:, :, :3] = (243, 240, 230)
Image.fromarray(a).save(OUT / "logo-light.png", optimize=True)

# Favicon und Vorschaubild auf Elfenbein
mark = Image.open(OUT / "logo-mark.png").convert("RGBA")
side = max(mark.size) + 44
fav = Image.new("RGBA", (side, side), (246, 244, 238, 255))
fav.alpha_composite(mark, ((side - mark.width) // 2, (side - mark.height) // 2))
fav.resize((256, 256), Image.LANCZOS).convert("RGB").save(ROOT / "favicon.png")
og = Image.new("RGBA", (1200, 630), (246, 244, 238, 255))
l = lg.copy(); l.thumbnail((820, 420))
og.alpha_composite(l, ((1200 - l.width) // 2, (630 - l.height) // 2))
og.convert("RGB").save(ROOT / "og-image.jpg", quality=88)
