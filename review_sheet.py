# -*- coding: utf-8 -*-
"""Собирает контрольный лист (contact sheet) для наглядного сравнения кадров."""
import os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "review")
os.makedirs(OUT, exist_ok=True)

def fit(im, box):
    im = im.convert("RGB")
    r = min(box[0] / im.width, box[1] / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)

def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

def sheet(items, out, cols=None, cell=(520, 640), title="Zaryanka style review"):
    cols = cols or len(items)
    rows = (len(items) + cols - 1) // cols
    pad, top = 16, 46
    W = pad + cols * (cell[0] + pad)
    H = top + pad + rows * (cell[1] + pad + 26)
    cv = Image.new("RGB", (W, H), (24, 26, 32))
    d = ImageDraw.Draw(cv)
    d.text((pad, 12), title, fill=(240, 240, 245), font=font(22))
    for i, (label, path) in enumerate(items):
        r, c = divmod(i, cols)
        x = pad + c * (cell[0] + pad)
        y = top + pad + r * (cell[1] + pad + 26)
        d.rectangle([x, y, x + cell[0], y + cell[1]], fill=(40, 42, 50))
        if path and os.path.exists(path):
            im = fit(Image.open(path), (cell[0], cell[1]))
            cv.paste(im, (x + (cell[0] - im.width) // 2, y + (cell[1] - im.height) // 2))
        d.text((x, y + cell[1] + 4), label, fill=(210, 214, 222), font=font(16))
    cv.save(out, "PNG")
    print("saved", out, cv.size)
    return out

if __name__ == "__main__":
    items = [
        ("2016 Спрайт — прямые (исходник)", os.path.join(HERE, "assets/src/c66f332fa5c9.png")),
        ("Эталон v1 — прямые (по спрайту)", os.path.join(HERE, "assets/gen/zaryanka_ref_0.png")),
        ("Эталон v2 — КУДРИ (по тексту)", os.path.join(HERE, "assets/gen/zaryanka_ref_curly_0.png")),
    ]
    sheet(items, os.path.join(OUT, "review_02_hair.png"), cols=3,
          cell=(560, 600), title="Зарянка — причёска: текст (кудри) vs спрайт 2016 (прямые)")
