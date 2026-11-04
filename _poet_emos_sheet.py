# -*- coding: utf-8 -*-
"""Лист эмоций поэта: база + 3 с длинными волосами + 3 стриженных; числа по лицам."""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
SAT = os.path.join(HERE, '_sat')
os.makedirs(SAT, exist_ok=True)


def f(name):
    for ext in ('.png', '.jpg'):
        p = os.path.join(GEN, name + '_0' + ext)
        if os.path.exists(p):
            return p
    return None


PANELS = [
    ('poet2_b_0.png', 'БАЗА (принята)'),
    ('poet_ha_neutral', 'длинные: нейтральное'),
    ('poet_ha_interested', 'длинные: заинтересованное'),
    ('poet_ha_upset', 'длинные: расстроенное'),
    ('poet_sh_neutral', 'стриженый: нейтральное'),
    ('poet_sh_tired', 'стриженый: утомлённое'),
    ('poet_sh_inspired', 'стриженый: одухотворённое'),
]

TH = 520
ims = []
for name, label in PANELS:
    p = os.path.join(GEN, name) if name.endswith('.png') else f(name)
    if not p or not os.path.exists(p):
        print('НЕТ', name)
        continue
    im = Image.open(p).convert('RGB')
    im = im.resize((int(im.width * TH / im.height), TH), Image.LANCZOS)
    ims.append((im, label, p))
    a = np.asarray(im.convert('L'), np.float32)
    h, w = a.shape
    face = a[int(h * 0.08):int(h * 0.42), int(w * 0.25):int(w * 0.75)]
    print('%-28s ярк %.0f  контраст %.0f  тёмных %.3f' % (label, face.mean(), face.std(),
                                                          float((face < 80).mean())))

pad, cap = 8, 24
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
except Exception:
    font = ImageFont.load_default()
row1, row2 = ims[:4], ims[4:]
W1 = sum(i.width for i, _, _ in row1) + pad * (len(row1) + 1)
W2 = sum(i.width for i, _, _ in row2) + pad * (len(row2) + 1)
W = max(W1, W2)
H = (TH + cap + pad) * 2 + pad
sheet = Image.new('RGB', (W, H), (24, 24, 28))
d = ImageDraw.Draw(sheet)
for ri, row in enumerate((row1, row2)):
    y = pad + ri * (TH + cap + pad)
    x = pad
    for im, label, _p in row:
        sheet.paste(im, (x, y))
        d.text((x + 3, y + TH + 3), label, fill=(235, 225, 205), font=font)
        x += im.width + pad
out = os.path.join(SAT, 'sheet_poet_emos.png')
sheet.save(out)
print('sheet ->', os.path.relpath(out, HERE), os.path.getsize(out), 'B')
