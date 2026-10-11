# -*- coding: utf-8 -*-
"""Лист выбора ГРЕЙДА пролога: как есть / полная сепия / тёплый архив.
Ответ на вопрос заказчика: «добавить сепии или не усложнять?».
Строит assets/review/review_58_prolog_grade.png. Ничего не перезаписывает (только лист).
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = os.path.join(HERE, 'assets', 'mock', 'prolog')
GEN = os.path.join(HERE, 'assets', 'gen')
OUT = os.path.join(HERE, 'assets', 'review', 'review_58_prolog_grade.png')
GOTH = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'

CM = np.array([[0.393, 0.769, 0.189],
               [0.349, 0.686, 0.168],
               [0.272, 0.534, 0.131]], float)


def sepia_full(a):
    return np.clip(a @ CM.T, 0, 255)


def warm_archive(a):
    """Тёплый архив-lite: 45% сепии + тёплый тинт + чуть контраста."""
    s = sepia_full(a)
    b = 0.45 * s + 0.55 * a
    b[..., 0] = np.clip(b[..., 0] * 1.035, 0, 255)
    b[..., 1] = np.clip(b[..., 1] * 1.005, 0, 255)
    b[..., 2] = np.clip(b[..., 2] * 0.930, 0, 255)
    b = np.clip((b - 128.0) * 1.07 + 128.0, 0, 255)
    return b


GRADES = [('A · как есть', lambda a: a),
          ('B · полная сепия (моно)', sepia_full),
          ('C · тёплый архив (реком.)', warm_archive)]


def compose(paths):
    base = Image.open(paths[0]).convert('RGB')
    for p in paths[1:]:
        ov = Image.open(p).convert('RGBA')
        base = Image.alpha_composite(base.convert('RGBA'), ov).convert('RGB')
    return base


ROWS = [
    (compose([os.path.join(MOCK, 's1_base.png')]),
     'S1 · подворотня (мок)'),
    (compose([os.path.join(MOCK, 's2_base.png')]),
     'S2 · космодром (мок)'),
    (compose([os.path.join(MOCK, 's5_base.png'), os.path.join(MOCK, 's5_posters.png')]),
     'S5 · лозунг: красные плакаты — что теряется в сепии'),
    (Image.open(os.path.join(GEN, 'prolog_s1_cin_0.jpg')).convert('RGB'),
     'S1 · кадр-проба flux-2 (кинохроника)'),
]

CW = 620
pad, gap, hdr, caph = 24, 12, 96, 40
panels = []
for im, cap in ROWS:
    im = im.resize((CW, round(im.height * CW / im.width)), Image.LANCZOS)
    panels.append((im, cap))
PH = panels[0][0].height
total_h = hdr + len(panels) * (PH + caph + gap) + pad
canvas = Image.new('RGB', (pad * 2 + 3 * CW + 2 * gap, total_h), (13, 14, 19))
d = ImageDraw.Draw(canvas)
d.text((pad, 16), '«ЗАРЯНКА» · пролог — выбор грейда (кинохроника)',
       font=ImageFont.truetype(GOTH, 30), fill=(226, 186, 104))
d.text((pad, 56), 'Сепия убивает красные плакаты S5 и золото значка. Рекомендую C — тёплый архив (цвет + архивный тон).',
       font=ImageFont.truetype(LATO_B, 21), fill=(206, 211, 230))

y = hdr
for im, cap in panels:
    x = pad
    for gname, fn in GRADES:
        arr = np.asarray(im, float)
        g = Image.fromarray(fn(arr).astype(np.uint8), 'RGB')
        canvas.paste(g, (x, y))
        d.rectangle([x, y, x + CW, y + PH], outline=(60, 62, 74))
        d.text((x + 4, y + PH - 28), gname, font=ImageFont.truetype(LATO_B, 19), fill=(238, 228, 200))
        x += CW + gap
    d.text((pad, y + PH + 6), cap, font=ImageFont.truetype(LATO_B, 22), fill=(240, 236, 228))
    y += PH + caph + gap

canvas.save(OUT)
print('saved', os.path.relpath(OUT, HERE), canvas.size)
