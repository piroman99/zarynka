# -*- coding: utf-8 -*-
"""Сравнение моделей на промпте «Сергей постарше»."""
import os, json
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "assets", "gen")
OUT = os.path.join(HERE, "assets", "review")
os.makedirs(OUT, exist_ok=True)

rep = json.load(open(os.path.join(GEN, "_sergey_eng_old_report.json"), encoding="utf-8"))

def fit(im, box):
    im = im.convert("RGB")
    r = min(box[0] / im.width, box[1] / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)

def font(sz):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()

# добавим прежний «молодой» вариант для сравнения
items = [("Сергей 33 (прошлый)", os.path.join(GEN, "sergey_eng_0.png"))]
for r in rep:
    if r.get("file"):
        lab = f"{r['model']} — {r['price']}₽ / {r['sec']}с"
        items.append((lab, os.path.join(HERE, r["file"])))

cell = (430, 560); cols = 3; pad, top = 16, 46
rows = (len(items) + cols - 1) // cols
W = pad + cols * (cell[0] + pad); H = top + pad + rows * (cell[1] + pad + 28)
cv = Image.new("RGB", (W, H), (24, 26, 32)); d = ImageDraw.Draw(cv)
d.text((pad, 12), "Сергей — «постарше»: сравнение моделей", fill=(240, 240, 245), font=font(22))
for i, (lab, p) in enumerate(items):
    r, c = divmod(i, cols)
    x = pad + c * (cell[0] + pad); y = top + pad + r * (cell[1] + pad + 28)
    d.rectangle([x, y, x + cell[0], y + cell[1]], fill=(40, 42, 50))
    if os.path.exists(p):
        im = fit(Image.open(p), cell)
        cv.paste(im, (x + (cell[0] - im.width) // 2, y + (cell[1] - im.height) // 2))
    d.text((x, y + cell[1] + 4), lab, fill=(210, 214, 222), font=font(15))
out = os.path.join(OUT, "review_05_sergey_age.png")
cv.save(out, "PNG"); print("saved", out, cv.size)
