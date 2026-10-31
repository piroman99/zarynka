# -*- coding: utf-8 -*-
"""Лист Ивану: кадр p8 v2 (гидролаборатория) — старый vs новый A/B + кропы модуля."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(HERE, "assets", "gen")
S = os.path.join(HERE, "_sat")
os.makedirs(S, exist_ok=True)

try:
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    fl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except Exception:
    f = fl = ImageFont.load_default()

A = os.path.join(G, "prolog_p8v2_a__gpt-image-2_0.png")
B = os.path.join(G, "prolog_p8v2_b__gpt-image-2_0.png")
OLD = os.path.join(G, "prolog_p8_pool__gpt-image-2_0.png")

items = [
    ("БЫЛО — макет «под Союз», глубина 12 м (Иван: старый модуль, надо футуристичнее)", OLD),
    ("A — с бортика: бассейн-шахта ~20 м, макет нового марсианского модуля на глубине", A),
    ("B — камера у воды: низ кадра подводный, модуль в глубине подсвечен", B),
]

cw, pad, top, lab = 1200, 16, 60, 30
first = Image.open(items[0][1])
ch = int(round(cw * first.size[1] / first.size[0]))
W = cw + 2 * pad
H = top + len(items) * (ch + lab + pad) + pad
cv = Image.new("RGB", (W, H), (14, 16, 22))
d = ImageDraw.Draw(cv)
d.text((pad, 18), "Зарянка · кадр p8 «гидролаборатория» — переделка (2026-10-31)",
       fill=(240, 240, 245), font=f)
y = top
for labt, p in items:
    im = Image.open(p).convert("RGB").resize((cw, ch), Image.LANCZOS)
    cv.paste(im, (pad, y))
    d.rectangle([pad, y, pad + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((pad, y + ch + 6), labt, fill=(212, 216, 224), font=fl)
    y += ch + lab + pad
out = os.path.join(S, "sheet_p8v2.png")
cv.save(out)
print("saved", out, cv.size)

# --- кропы модуля в нативном разрешении (проверка букв и деталей) ---
# модуль висит примерно в середине кадра; берём центр по ширине и середину по высоте
crops = []
for tag, p in (("A", A), ("B", B)):
    im = Image.open(p).convert("RGB")
    w, h = im.size
    box = (int(w * 0.20), int(h * 0.28), int(w * 0.80), int(h * 0.95))
    c = im.crop(box)
    crops.append((tag + " · модуль, кроп в нативе", c))

cw2 = 1100
ch2 = int(round(cw2 * crops[0][1].size[1] / crops[0][1].size[0]))
H2 = top + len(crops) * (ch2 + lab + pad) + pad
cv2 = Image.new("RGB", (cw2 + 2 * pad, H2), (14, 16, 22))
d2 = ImageDraw.Draw(cv2)
d2.text((pad, 18), "p8 v2 · детали модуля в нативном разрешении (буквы/эмблемы)",
        fill=(240, 240, 245), font=f)
y = top
for labt, c in crops:
    c = c.resize((cw2, ch2), Image.LANCZOS)
    cv2.paste(c, (pad, y))
    d2.rectangle([pad, y, pad + cw2 - 1, y + ch2 - 1], outline=(48, 52, 64))
    d2.text((pad, y + ch2 + 6), labt, fill=(212, 216, 224), font=fl)
    y += ch2 + lab + pad
out2 = os.path.join(S, "sheet_p8v2_detail.png")
cv2.save(out2)
print("saved", out2, cv2.size)

# --- уменьшенные копии для чата ---
for src, dst, w2 in ((out, "sheet_p8v2_small.jpg", 900),
                     (out2, "sheet_p8v2_detail_small.jpg", 900)):
    im = Image.open(src).convert("RGB")
    im = im.resize((w2, int(round(w2 * im.size[1] / im.size[0]))), Image.LANCZOS)
    p = os.path.join(S, dst)
    im.save(p, quality=88)
    print("saved", p, im.size)