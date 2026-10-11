# -*- coding: utf-8 -*-
"""P0 — лист «смотреть до дела»: значок 3D (лицо/рёбра/оборот) + макро гравировки на ребре.
Гравировка сокращена до «ЛМД» (правка заказчика 2026-10-11). Выход: assets/review/review_61_znak3d_review.png.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REVIEW = os.path.join(HERE, 'assets', 'review')
OUT = os.path.join(REVIEW, 'review_61_znak3d_review.png')
GOTH = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'

_src = open(os.path.join(HERE, '_znak3d.py')).read().split("if '--sheet' in sys.argv:")[0]
_ns = {'__file__': os.path.join(HERE, '_znak3d.py'), '__name__': 'z3d'}
exec(compile(_src, '_znak3d.py', 'exec'), _ns)
render, RIB_TEXT = _ns['render'], _ns['RIB_TEXT']

ANGLES = [(0, '0° · лицо'), (45, '45° · разворот'), (90, '90° · РЕБРО'),
          (135, '135° · оборот идёт'), (180, '180° · оборот-иллюминатор')]
CW = 360
pad, gap, hdr, caph = 22, 12, 96, 40
imgs = []
for a, cap in ANGLES:
    im = render(a, w=1000, h=1000).resize((CW, CW), Image.LANCZOS)
    imgs.append((im, cap))

# макро ребра (90°) — с новой гравировкой
im90 = render(90, w=1280, h=1280)
arr = np.asarray(im90)
fg = (np.abs(arr.astype(int) - np.array([6, 8, 18])).sum(axis=2) > 24)
ys, xs = np.where(fg)
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
crop = im90.crop((max(0, x0 - 44), max(0, y0 - 16), min(1280, x1 + 44), min(1280, y1 + 16)))
sc = 620 / crop.height
macro = crop.resize((max(1, int(crop.width * sc)), 620), Image.LANCZOS)

BW = pad * 2 + 5 * CW + 4 * gap
BH = hdr + CW + caph + 24 + 620 + 44 + pad
canvas = Image.new('RGB', (BW, BH), (13, 14, 19))
d = ImageDraw.Draw(canvas)
d.text((pad, 16), '«ЗАРЯНКА» · P0 значок — смотреть до дела (3D + гравировка)',
       font=ImageFont.truetype(GOTH, 30), fill=(226, 186, 104))
d.text((pad, 56), 'Гравировка на ребре сокращена до «%s» (без цены). Черновик вращения: out/znak3d_rot_draft.mp4' % RIB_TEXT,
       font=ImageFont.truetype(LATO_B, 21), fill=(206, 211, 230))

y = hdr
x = pad
for im, cap in imgs:
    canvas.paste(im, (x, y))
    d.rectangle([x, y, x + CW, y + CW], outline=(60, 62, 74))
    d.text((x + 6, y + CW + 8), cap, font=ImageFont.truetype(LATO_B, 21), fill=(240, 236, 228))
    x += CW + gap

y = hdr + CW + caph + 10
d.text((pad, y), 'МАКРО РЕБРА (90°) — гравировка «%s»' % RIB_TEXT,
       font=ImageFont.truetype(LATO_B, 22), fill=(150, 205, 150))
cx = pad + (BW - 2 * pad - macro.width) // 2
canvas.paste(macro, (cx, y + 34))
d.rectangle([cx, y + 34, cx + macro.width, y + 34 + macro.height], outline=(80, 82, 96))
canvas.save(OUT)
print('saved', os.path.relpath(OUT, HERE), canvas.size)
