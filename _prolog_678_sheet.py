# -*- coding: utf-8 -*-
"""Лист Ивану: кадры пролога 6 / 7 / 8 (план 2026-10-25, плотная сетка кадров)."""
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
    ("6 · ХРОНИКА ПЕРВОГО ПОЛЁТА — проводы Первой марсианской экспедиции, плёнка заметно старше",
     os.path.join(GEN, "prolog_p6_firstflight__gpt-image-2_0.png")),
    ("7 · ЦЕХ СБОРКИ — НОВАЯ ракета недостроена (нижний пояс, шпангоуты, леса), тот же цех, что S2",
     os.path.join(GEN, "prolog_p7_ceh_new__gpt-image-2_0.png")),
    ("8 · БАССЕЙН-ГИДРОЛАБОРАТОРИЯ — макет модуля на глубине, космонавты в скафандрах",
     os.path.join(GEN, "prolog_p8_pool__gpt-image-2_0.png")),
]

cw, pad, top, lab = 1280, 16, 56, 30
first = Image.open(items[0][1])
ch = int(round(cw * first.size[1] / first.size[0]))
W = cw + 2 * pad
H = top + len(items) * (ch + lab + pad) + pad
cv = Image.new("RGB", (W, H), (14, 16, 22))
d = ImageDraw.Draw(cv)
d.text((pad, 16), "Зарянка · пролог, кадры 6-8 (gpt-image-2, 12.18 ₽)", fill=(240, 240, 245), font=f)

y = top
for labt, p in items:
    im = Image.open(p).convert("RGB").resize((cw, ch), Image.LANCZOS)
    cv.paste(im, (pad, y))
    d.rectangle([pad, y, pad + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((pad, y + ch + 5), labt, fill=(212, 216, 224), font=fl)
    y += ch + lab + pad

out = os.path.join(OUT, "sheet_p678.png")
cv.save(out)
print("saved", out, cv.size)

# деталь в нативе: левый и правый край каждого кадра (буквы/артефакты)
crops = []
for labt, p in items:
    im = Image.open(p).convert("RGB")
    w, h = im.size
    half = w // 2
    crops.append((labt.split("—")[0].strip() + " · левая половина, натив",
                  im.crop((0, 0, half, h))))
    crops.append((labt.split("—")[0].strip() + " · правая половина, натив",
                  im.crop((half, 0, w, h))))

pad2, top2 = 14, 50
cw2 = max(c.size[0] for _, c in crops)
H2 = top2 + sum(c.size[1] + 26 + pad2 for _, c in crops) + pad2
cv2 = Image.new("RGB", (cw2 + 2 * pad2, H2), (14, 16, 22))
d2 = ImageDraw.Draw(cv2)
d2.text((pad2, 14), "Кадры 6-8 · нативное разрешение (проверка букв и артефактов)",
        fill=(240, 240, 245), font=f)
y = top2
for labt, c in crops:
    cv2.paste(c, (pad2, y))
    d2.rectangle([pad2, y, pad2 + c.size[0] - 1, y + c.size[1] - 1], outline=(48, 52, 64))
    d2.text((pad2, y + c.size[1] + 4), labt, fill=(212, 216, 224), font=fl)
    y += c.size[1] + 26 + pad2
out2 = os.path.join(OUT, "sheet_p678_detail.png")
cv2.save(out2)
print("saved", out2, cv2.size)
