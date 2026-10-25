# -*- coding: utf-8 -*-
"""Лист Ивану: кадр 6 «хроника с Марса», варианты A/B + деталь в нативе."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "assets", "gen")
OUT = os.path.join(HERE, "_sat")
os.makedirs(OUT, exist_ok=True)

try:
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    fl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 19)
except Exception:
    f = fl = ImageFont.load_default()

items = [
    ("A · общий — корабль на равнине, крошечный экипаж, кратер",
     os.path.join(GEN, "prolog_p6_mars_a__gpt-image-2_0.png")),
    ("B · средний план — двое в старых скафандрах идут по пыли, корабль силуэтом позади",
     os.path.join(GEN, "prolog_p6_mars_b__gpt-image-2_0.png")),
]

cw, pad, top, lab = 1280, 16, 56, 30
first = Image.open(items[0][1])
ch = int(round(cw * first.size[1] / first.size[0]))
W = cw + 2 * pad
H = top + len(items) * (ch + lab + pad) + pad
cv = Image.new("RGB", (W, H), (14, 16, 22))
d = ImageDraw.Draw(cv)
d.text((pad, 16), "Зарянка · кадр 6 «хроника первого полёта» — кадры С МАРСА (A/B, 5.40 ₽)",
       fill=(240, 240, 245), font=f)
y = top
for labt, p in items:
    im = Image.open(p).convert("RGB").resize((cw, ch), Image.LANCZOS)
    cv.paste(im, (pad, y))
    d.rectangle([pad, y, pad + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((pad, y + ch + 5), labt, fill=(212, 216, 224), font=fl)
    y += ch + lab + pad
out = os.path.join(OUT, "sheet_p6_mars.png")
cv.save(out)
print("saved", out, cv.size)

# деталь: левая и правая половина каждого кадра в нативном разрешении
crops = []
for labt, p in items:
    im = Image.open(p).convert("RGB")
    w, h = im.size
    tag = labt.split("·")[0].strip()
    crops.append((tag + " · левая половина, натив", im.crop((0, 0, w // 2, h))))
    crops.append((tag + " · правая половина, натив", im.crop((w // 2, 0, w, h))))
pad2, top2 = 14, 50
cw2 = max(c.size[0] for _, c in crops)
H2 = top2 + sum(c.size[1] + 26 + pad2 for _, c in crops) + pad2
cv2 = Image.new("RGB", (cw2 + 2 * pad2, H2), (14, 16, 22))
d2 = ImageDraw.Draw(cv2)
d2.text((pad2, 14), "Кадр 6 с Марса · нативное разрешение (буквы, эмблемы, артефакты)",
        fill=(240, 240, 245), font=f)
y = top2
for labt, c in crops:
    cv2.paste(c, (pad2, y))
    d2.rectangle([pad2, y, pad2 + c.size[0] - 1, y + c.size[1] - 1], outline=(48, 52, 64))
    d2.text((pad2, y + c.size[1] + 4), labt, fill=(212, 216, 224), font=fl)
    y += c.size[1] + 26 + pad2
out2 = os.path.join(OUT, "sheet_p6_mars_detail.png")
cv2.save(out2)
print("saved", out2, cv2.size)

for name, w in (("sheet_p6_mars.png", 780), ("sheet_p6_mars_detail.png", 700)):
    im = Image.open(os.path.join(OUT, name)).convert("RGB")
    h = int(round(w * im.size[1] / im.size[0]))
    dst = os.path.join(OUT, name.replace(".png", "_small.jpg"))
    im.resize((w, h), Image.LANCZOS).save(dst, quality=88)
    print("saved", dst, (w, h))
