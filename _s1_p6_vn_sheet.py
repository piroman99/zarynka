# -*- coding: utf-8 -*-
"""Лист Ивану: кадр s1 (стена → подворотня) и кадр p6 (лунная станция) в движке.

    python3 _s1_p6_vn_sheet.py

Вход — скриншоты `_shot_s1_p6.py` (`_sat/s1_p0_wall.png`, `s1_p1_alley.png`,
`p6_p0.png`, `p6_p1.png`). Выход — `_sat/sheet_s1_p6_vn.png` + `_small.jpg`.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(HERE, '_sat')

try:
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 26)
    fl = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
except Exception:
    f = fl = ImageFont.load_default()

items = [
    ('s1 · стр. 1 — «Кто бросил клич „Марс — дело общее“?» (новый кадр: стена, граффити)',
     's1_p0_wall.png'),
    ('s1 · стр. 2 — «…поймать умника в темной подворотне» (прежний кадр, котобус мелом)',
     's1_p1_alley.png'),
    ('p6 · стр. 1 — «Вторая Марсианская…» (НОВЫЙ кадр: лунная станция, без композита)',
     'p6_p0.png'),
    ('p6 · стр. 2 — «…лучше лунную базу до ума доведите» (та же станция)',
     'p6_p1.png'),
]

cw, pad, top, lab = 1200, 16, 56, 30
missing = [n for _, n in items if not os.path.exists(os.path.join(S, n))]
if missing:
    raise SystemExit('нет скриншотов: %s (сначала _shot_s1_p6.py)' % ', '.join(missing))

first = Image.open(os.path.join(S, items[0][1]))
ch = int(round(cw * first.size[1] / first.size[0]))
W = cw + 2 * pad
H = top + len(items) * (ch + lab + pad) + pad
cv = Image.new('RGB', (W, H), (14, 16, 22))
d = ImageDraw.Draw(cv)
d.text((pad, 14), 'Зарянка · кадр s1 (стена → подворотня) и кадр p6 (лунная станция)',
       fill=(240, 240, 245), font=f)
y = top
for cap, name in items:
    im = Image.open(os.path.join(S, name)).convert('RGB').resize((cw, ch), Image.LANCZOS)
    cv.paste(im, (pad, y))
    d.rectangle([pad, y, pad + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((pad, y + ch + 4), cap, fill=(212, 216, 224), font=fl)
    y += ch + lab + pad

out = os.path.join(S, 'sheet_s1_p6_vn.png')
cv.save(out)
sm = os.path.join(S, 'sheet_s1_p6_vn_small.jpg')
cv.convert('RGB').resize((W // 2, H // 2), Image.LANCZOS).save(sm, quality=88)
print('лист -> %s (%dx%d)' % (out, W, H))
print('малый -> %s' % sm)
