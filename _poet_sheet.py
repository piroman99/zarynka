# -*- coding: utf-8 -*-
"""Лист спрайтов поэта + числа: годен ли фон под cutout() (ровный светлый бордюр)."""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
SAT = os.path.join(HERE, '_sat')
os.makedirs(SAT, exist_ok=True)

PANELS = [
    (os.path.join(GEN, 'sergey_eng_old__flux-2_0.jpg'), 'эталон каста: Сергей'),
    (os.path.join(GEN, 'kate_overalls_0.png'), 'эталон каста: Екатерина'),
    (os.path.join(GEN, 'poet_a_0.png'), 'ПОЭТ — вариант A'),
    (os.path.join(GEN, 'poet_b_0.png'), 'ПОЭТ — вариант B'),
]

for p, label in PANELS[2:]:
    a = np.asarray(Image.open(p).convert('RGB'), np.int16)
    h, w, _ = a.shape
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg = np.median(border, axis=0)
    d = np.abs(a - bg).max(2)
    print('%-22s %dx%d  фон(медиана) %s  бордюр разброс %.0f  фон-доля %.3f  тёмных %.3f'
          % (os.path.basename(p), w, h, bg.tolist(), border.std(0).mean(),
             float((d < 22).mean()), float((a.mean(2) < 90).mean())))

TH = 640
ims = []
for p, label in PANELS:
    im = Image.open(p).convert('RGB')
    im = im.resize((int(im.width * TH / im.height), TH), Image.LANCZOS)
    ims.append((im, label))
pad, cap = 8, 24
W = sum(i.width for i, _ in ims) + pad * (len(ims) + 1)
sheet = Image.new('RGB', (W, TH + cap + pad * 2), (24, 24, 28))
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
except Exception:
    font = ImageFont.load_default()
x = pad
for im, label in ims:
    sheet.paste(im, (x, pad))
    d.text((x + 3, pad + TH + 3), label, fill=(235, 225, 205), font=font)
    x += im.width + pad
out = os.path.join(SAT, 'sheet_poet.png')
sheet.save(out)
print('sheet ->', os.path.relpath(out, HERE), os.path.getsize(out), 'B')
