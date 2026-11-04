# -*- coding: utf-8 -*-
"""Лист и числа по фонам сцены «аллея у ворот» (assets/gen/steps_a|alley_a|alley_b)."""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
SAT = os.path.join(HERE, '_sat')
os.makedirs(SAT, exist_ok=True)

FILES = [('steps_a', '1. ДВЕРИ И СТУПЕНИ — A'),
         ('alley_a', '2. АЛЛЕЯ И СКАМЕЙКА — A'),
         ('alley_b', '3. АЛЛЕЯ И СКАМЕЙКА — B (шире)')]
REF = (os.path.join(HERE, 'assets', 'pilot', 'pilot_reception_0.png'),
       '0. ЭТАЛОН стиля — приёмная')


def stats(path):
    im = Image.open(path).convert('RGB')
    a = np.asarray(im, np.float32)
    mx = a.max(2)
    mn = a.min(2)
    sat = (mx - mn) / np.maximum(mx, 1)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    # охра: красный заметно выше синего
    ochre = float(((r - b > 28) & (r > 90)).mean())
    # «бумага»: очень светлые, почти бесцветные пиксели
    paper = float(((mx > 232) & (sat < 0.10)).mean())
    # зелень елей: зелёный выше красного и синего, но не яркая
    green = float(((g > r + 6) & (g > b + 6) & (mx < 190)).mean())
    return dict(size=im.size, bright=float(a.mean()), sat=float(sat.mean()),
                ochre=ochre, paper=paper, green=green)


rows = []
for name, label in FILES:
    p = os.path.join(GEN, name + '_0.png')
    if not os.path.exists(p):
        p = os.path.join(GEN, name + '_0.jpg')
    s = stats(p)
    rows.append((name, label, p, s))
    print('%-8s %sx%s  ярк %.0f  насыщ %.2f  охра %.3f  бумага %.3f  ель %.3f'
          % (name, s['size'][0], s['size'][1], s['bright'], s['sat'], s['ochre'],
             s['paper'], s['green']))

W, H = 1600, 900
scale = 0.42
tw, th = int(W * scale), int(H * scale)
pad, cap = 8, 24
panels = [(REF[0], REF[1])] + [(r[2], r[1]) for r in rows]
sheet = Image.new('RGB', (tw * len(panels) + pad * (len(panels) + 1), th + cap + pad * 2), (18, 18, 22))
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
except Exception:
    font = ImageFont.load_default()
x = pad
for p, label in panels:
    im = Image.open(p).convert('RGB').resize((tw, th), Image.LANCZOS)
    sheet.paste(im, (x, pad))
    d.text((x + 3, pad + th + 4), label, fill=(235, 225, 205), font=font)
    x += tw + pad
out = os.path.join(SAT, 'sheet_alley_bg.png')
sheet.save(out)
print('sheet ->', os.path.relpath(out, HERE), os.path.getsize(out), 'B')
