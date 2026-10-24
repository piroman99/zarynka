# -*- coding: utf-8 -*-
"""Лист для Ивана: посвящение, титры-ролл (3 фазы), конец серии, CG-страница 48."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
SAT = os.path.join(HERE, '_sat')

items = [
    ('Посвящение (после лого-значка)', 'new_ded.png'),
    ('Титры · начало ролла', 'new_cr_a.png'),
    ('Титры · середина', 'new_cr_b.png'),
    ('Титры · финал', 'new_cr_c.png'),
    ('Конец серии (после титров)', 'new_end.png'),
    ('Приёмная, стр. 48 — CG вариант А', 'new_rec48.png'),
]

cw, ch, cols = 760, 428, 2
pad, top = 18, 54
rows = (len(items) + cols - 1) // cols
W = pad + cols * (cw + pad)
H = top + rows * (ch + pad + 30) + pad
cv = Image.new('RGB', (W, H), (12, 14, 20))
d = ImageDraw.Draw(cv)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
fl = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
d.text((pad, 15), 'Зарянка · посвящение, титры-ролл и CG стр.48 (2026-10-24)', fill=(240, 240, 245), font=f)
for i, (lab, fn) in enumerate(items):
    c, r = i % cols, i // cols
    x = pad + c * (cw + pad)
    y = top + r * (ch + pad + 30)
    p = os.path.join(SAT, fn)
    if not os.path.exists(p):
        d.text((x + 10, y + 10), 'нет: ' + fn, fill=(220, 120, 120), font=fl)
        continue
    im = Image.open(p).convert('RGB')
    im.thumbnail((cw, ch), Image.LANCZOS)
    cv.paste(im, (x + (cw - im.width) // 2, y + (ch - im.height) // 2))
    d.rectangle([x, y, x + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((x, y + ch + 6), lab, fill=(214, 218, 226), font=fl)
out = os.path.join(SAT, 'sheet_ded_credits.png')
cv.save(out)
print('saved', out, cv.size)
