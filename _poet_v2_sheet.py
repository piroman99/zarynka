# -*- coding: utf-8 -*-
"""Лист: каст (Сергей, Екатерина) + поэт v1 (аниме) + поэт v2 (округлое лицо, щетина)."""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
SAT = os.path.join(HERE, '_sat')
os.makedirs(SAT, exist_ok=True)

PANELS = [
    (os.path.join(GEN, 'sergey_eng_old__flux-2_0.jpg'), 'каст: Сергей'),
    (os.path.join(GEN, 'kate_overalls_0.png'), 'каст: Екатерина'),
    (os.path.join(GEN, 'poet_b_0.png'), 'поэт v1 (аниме) — ОТКАЗ'),
    (os.path.join(GEN, 'poet2_a_0.png'), 'поэт v2 — A'),
    (os.path.join(GEN, 'poet2_b_0.png'), 'поэт v2 — B'),
]

TH = 620
ims = []
for p, label in PANELS:
    im = Image.open(p).convert('RGB')
    im = im.resize((int(im.width * TH / im.height), TH), Image.LANCZOS)
    ims.append((im, label))

# кропы лиц: верхняя треть кадра, крупно
FACES = [(os.path.join(GEN, n), lbl) for n, lbl in
         (('poet_b_0.png', 'v1 лицо (аниме)'), ('poet2_a_0.png', 'v2-A лицо'),
          ('poet2_b_0.png', 'v2-B лицо'))]
faces = []
FH = 380
for p, label in FACES:
    im = Image.open(p).convert('RGB')
    w, h = im.size
    box = (int(w * 0.18), int(h * 0.04), int(w * 0.82), int(h * 0.04 + w * 0.64))
    c = im.crop(box)
    c = c.resize((int(c.width * FH / c.height), FH), Image.LANCZOS)
    faces.append((c, label))
    a = np.asarray(c.convert('L'), np.float32)
    # «мягкость» лица: доля средних тонов против резких тёмных линий (лайн-арт)
    dark = float((a < 70).mean())
    mid = float(((a >= 70) & (a < 190)).mean())
    print('%-16s тёмных %.3f  средних %.3f  контраст %.0f' % (label, dark, mid, a.std()))

pad, cap = 8, 24
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
except Exception:
    font = ImageFont.load_default()

W1 = sum(i.width for i, _ in ims) + pad * (len(ims) + 1)
W2 = sum(i.width for i, _ in faces) + pad * (len(faces) + 1)
W = max(W1, W2)
H = (TH + cap + pad) * 2 + pad
sheet = Image.new('RGB', (W, H), (24, 24, 28))
d = ImageDraw.Draw(sheet)
x = pad
for im, label in ims:
    sheet.paste(im, (x, pad))
    d.text((x + 3, pad + TH + 3), label, fill=(235, 225, 205), font=font)
    x += im.width + pad
y = pad + TH + cap + pad
x = pad
for im, label in faces:
    sheet.paste(im, (x, y))
    d.text((x + 3, y + FH + 3), label, fill=(235, 225, 205), font=font)
    x += im.width + pad
out = os.path.join(SAT, 'sheet_poet_v2.png')
sheet.save(out)
print('sheet ->', os.path.relpath(out, HERE), os.path.getsize(out), 'B')
