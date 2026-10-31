# -*- coding: utf-8 -*-
"""Лист Ивану: p8 v4 — остекление на межпланетном корабле (правка принятого B)."""
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

BASE = os.path.join(G, "prolog_p8v3_b__gpt-image-2_0.png")
A = os.path.join(G, "prolog_p8v4_a__gpt-image-2_0.png")
B = os.path.join(G, "prolog_p8v4_b__gpt-image-2_0.png")

items = [
    ("БЫЛО — принятый B: на корабле окон нет (Иван: «нет иллюминаторов или лобовых стёкол»)", BASE),
    ("A — сдержанно: лента лобового остекления + один ряд иллюминаторов", A),
    ("B — выразительнее: лента лобовых окон + два ряда иллюминаторов, тёплый свет внутри", B),
]

cw, pad, top, lab = 1200, 16, 60, 30
first = Image.open(items[0][1])
ch = int(round(cw * first.size[1] / first.size[0]))
W = cw + 2 * pad
H = top + len(items) * (ch + lab + pad) + pad
cv = Image.new("RGB", (W, H), (14, 16, 22))
d = ImageDraw.Draw(cv)
d.text((pad, 18), "Зарянка · кадр p8 v4 — остекление межпланетного корабля",
       fill=(240, 240, 245), font=f)
y = top
for labt, p in items:
    im = Image.open(p).convert("RGB").resize((cw, ch), Image.LANCZOS)
    cv.paste(im, (pad, y))
    d.rectangle([pad, y, pad + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((pad, y + ch + 6), labt, fill=(212, 216, 224), font=fl)
    y += ch + lab + pad
out = os.path.join(S, "sheet_p8v4.png")
cv.save(out)
print("saved", out, cv.size)

# кропы в нативном разрешении: нос и корпус (проверка букв на стекле/корпусе)
crops = []
for tag, p, box in (("A · натив, нос и корпус", A, (0.10, 0.05, 0.78, 0.80)),
                    ("B · натив, нос и корпус", B, (0.10, 0.05, 0.78, 0.80))):
    im = Image.open(p).convert("RGB")
    w, h = im.size
    crops.append((tag, im.crop((int(w * box[0]), int(h * box[1]),
                                int(w * box[2]), int(h * box[3])))))

cw2 = 1150
H2 = top + sum(int(round(cw2 * c.size[1] / c.size[0])) + lab + pad for _, c in crops) + pad
cv2 = Image.new("RGB", (cw2 + 2 * pad, H2), (14, 16, 22))
d2 = ImageDraw.Draw(cv2)
d2.text((pad, 18), "p8 v4 · окна в нативном разрешении (буквы на стекле и корпусе)",
        fill=(240, 240, 245), font=f)
y = top
for labt, c in crops:
    ch2 = int(round(cw2 * c.size[1] / c.size[0]))
    c = c.resize((cw2, ch2), Image.LANCZOS)
    cv2.paste(c, (pad, y))
    d2.rectangle([pad, y, pad + cw2 - 1, y + ch2 - 1], outline=(48, 52, 64))
    d2.text((pad, y + ch2 + 6), labt, fill=(212, 216, 224), font=fl)
    y += ch2 + lab + pad
out2 = os.path.join(S, "sheet_p8v4_detail.png")
cv2.save(out2)
print("saved", out2, cv2.size)

for src, dst, w2 in ((out, "sheet_p8v4_small.jpg", 900),
                     (out2, "sheet_p8v4_detail_small.jpg", 900)):
    im = Image.open(src).convert("RGB")
    im = im.resize((w2, int(round(w2 * im.size[1] / im.size[0]))), Image.LANCZOS)
    p = os.path.join(S, dst)
    im.save(p, quality=88)
    print("saved", p, im.size)