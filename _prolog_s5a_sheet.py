# -*- coding: utf-8 -*-
"""Лист Ивану: кадр 11 (s5a) A/B — городская площадь с плакатными тумбами + кропы в нативе."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "assets", "gen")
OUT = os.path.join(HERE, "_sat")
os.makedirs(OUT, exist_ok=True)

items = [
    ("A · камера на уровне глаз, двое клеят плакат крупно слева",
     os.path.join(GEN, "s5a_a__gpt-image-2_0.png")),
    ("B · общий план площади, тумбы и стенд-витрина",
     os.path.join(GEN, "s5a_b__gpt-image-2_0.png")),
]

try:
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    fl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except Exception:
    f = fl = ImageFont.load_default()

for _, p in items:
    im = Image.open(p)
    print(os.path.basename(p), im.size, im.mode)

cw, pad, top, lab = 1280, 16, 56, 30
im0 = Image.open(items[0][1])
ch = int(round(cw * im0.size[1] / im0.size[0]))
W = cw + 2 * pad
H = top + len(items) * (ch + lab + pad) + pad
cv = Image.new("RGB", (W, H), (14, 16, 22))
d = ImageDraw.Draw(cv)
d.text((pad, 16), "Зарянка · кадр 11 (s5a) — площадь с плакатными тумбами, плакаты ПУСТЫЕ",
       fill=(240, 240, 245), font=f)
y = top
for labt, p in items:
    im = Image.open(p).convert("RGB").resize((cw, ch), Image.LANCZOS)
    cv.paste(im, (pad, y))
    d.rectangle([pad, y, pad + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((pad, y + ch + 5), labt, fill=(212, 216, 224), font=fl)
    y += ch + lab + pad
out1 = os.path.join(OUT, "sheet_s5a.png")
cv.save(out1)
print("saved", out1, cv.size)

# --- нативные кропы: центр (тумбы/плакаты) и левый край, где клеят ---
crops = []
for labt, p in items:
    im = Image.open(p).convert("RGB")
    w, h = im.size
    crops.append((labt + " · центр-лево, натив", im.crop((int(w * 0.02), int(h * 0.10), int(w * 0.62), int(h * 0.92)))))
    crops.append((labt + " · право, натив", im.crop((int(w * 0.55), int(h * 0.20), int(w * 0.99), int(h * 0.92)))))

pad2, top2 = 14, 48
cw2 = max(c.size[0] for _, c in crops)
W2 = cw2 + 2 * pad2
H2 = top2 + sum(c.size[1] + 26 + pad2 for _, c in crops) + pad2
cv2 = Image.new("RGB", (W2, H2), (14, 16, 22))
d2 = ImageDraw.Draw(cv2)
d2.text((pad2, 14), "s5a · нативные кропы (проверка: плакаты без букв, тумбы, люди)", fill=(240, 240, 245), font=f)
y = top2
for labt, c in crops:
    cv2.paste(c, (pad2, y))
    d2.rectangle([pad2, y, pad2 + c.size[0] - 1, y + c.size[1] - 1], outline=(48, 52, 64))
    d2.text((pad2, y + c.size[1] + 4), labt, fill=(212, 216, 224), font=fl)
    y += c.size[1] + 26 + pad2
out2 = os.path.join(OUT, "crops_s5a.png")
cv2.save(out2)
print("saved", out2, cv2.size)
