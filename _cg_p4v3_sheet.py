# -*- coding: utf-8 -*-
"""Лист Ивану: P4 v3 A/B (Сергей со спрайта: щетина, жилет, бейдж) + кропы в нативе."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "assets", "gen")
OUT = os.path.join(HERE, "_sat")
os.makedirs(OUT, exist_ok=True)

A = os.path.join(GEN, "cg_p4v3_a__gpt-image-2_0.png")
B = os.path.join(GEN, "cg_p4v3_b__gpt-image-2_0.png")

try:
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    fl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except Exception:
    f = fl = ImageFont.load_default()

items = [("A · средний план от окна (Сергей справа)", A),
         ("B · через плечо Екатерины (Сергей в фокусе)", B)]

# --- лист: два кадра полными полосами ---
cw, pad, top, lab = 1280, 16, 56, 30
ch = None
for _, p in items:
    im = Image.open(p)
    ch = int(round(cw * im.size[1] / im.size[0]))
    break
W = cw + 2 * pad
H = top + len(items) * (ch + lab + pad) + pad
cv = Image.new("RGB", (W, H), (14, 16, 22))
d = ImageDraw.Draw(cv)
d.text((pad, 16), "Зарянка · P4 v3 — Сергей ОДИН В ОДИН со спрайта (щетина, жилет, бейдж «ИНЖЕНЕР»)",
       fill=(240, 240, 245), font=f)
y = top
for labt, p in items:
    im = Image.open(p).convert("RGB").resize((cw, ch), Image.LANCZOS)
    cv.paste(im, (pad, y))
    d.rectangle([pad, y, pad + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((pad, y + ch + 5), labt, fill=(212, 216, 224), font=fl)
    y += ch + lab + pad
out1 = os.path.join(OUT, "sheet_p4v3.png")
cv.save(out1)
print("saved", out1, cv.size)

# --- детали: кропы в НАТИВНОМ разрешении (проверка щетины/жилета/букв на бейдже) ---
crops = []
for labt, p in items:
    im = Image.open(p).convert("RGB")
    w, h = im.size
    # правая часть кадра, где Сергей; натив, без ресайза
    box = (int(w * 0.46), int(h * 0.06), int(w * 0.99), int(h * 0.94))
    c = im.crop(box)
    crops.append((labt + " · натив, правая часть", c))

pad2 = 14
cw2 = max(c.size[0] for _, c in crops)
top2 = 50
W2 = cw2 + 2 * pad2
H2 = top2 + sum(c.size[1] + 26 + pad2 for _, c in crops) + pad2
cv2 = Image.new("RGB", (W2, H2), (14, 16, 22))
d2 = ImageDraw.Draw(cv2)
d2.text((pad2, 14), "P4 v3 · детали в нативном разрешении", fill=(240, 240, 245), font=f)
y = top2
for labt, c in crops:
    cv2.paste(c, (pad2, y))
    d2.rectangle([pad2, y, pad2 + c.size[0] - 1, y + c.size[1] - 1], outline=(48, 52, 64))
    d2.text((pad2, y + c.size[1] + 4), labt, fill=(212, 216, 224), font=fl)
    y += c.size[1] + 26 + pad2
out2 = os.path.join(OUT, "sheet_p4v3_detail.png")
cv2.save(out2)
print("saved", out2, cv2.size)
