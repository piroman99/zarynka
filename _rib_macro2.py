# -*- coding: utf-8 -*-
"""P0 — МАКРО гравировки на ребре («ЛМД») + кадр «наезда» для показа до дела.
Рендер большого значка при 90° и кроп рёбра. Выход: assets/review/review_63_rib_macro.png.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, 'assets', 'review')
OUT = os.path.join(REV, 'review_63_rib_macro.png')
GOTH = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'

src = open(os.path.join(HERE, '_znak3d.py')).read().split("if '--sheet' in sys.argv:")[0]
ns = {'__file__': os.path.join(HERE, '_znak3d.py'), '__name__': 'z3d'}
exec(compile(src, '_znak3d.py', 'exec'), ns)
render, RIB_TEXT, RIB_FACE = ns['render'], ns['RIB_TEXT'], ns['RIB_FACE']

BIG = 6000
im = render(90, w=BIG, h=BIG)
arr = np.asarray(im)
fg = (np.abs(arr.astype(int) - np.array([6, 8, 18])).sum(axis=2) > 24)
ys, xs = np.where(fg)
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
print('ребро 90°: w=%d h=%d (rib_face=%d)' % (x1 - x0 + 1, y1 - y0 + 1, RIB_FACE))
crop = im.crop((max(0, x0 - 60), max(0, y0 - 30), min(BIG, x1 + 60), min(BIG, y1 + 30)))

# вписать в высоту 900
sc = 900 / crop.height
crop = crop.resize((max(1, int(crop.width * sc)), 900), Image.LANCZOS)

# также «широкий» вид: как выглядит ребро в кадре 16:9 (мелко) — для сравнения
wide = render(90, w=1920, h=1920).crop((0, 420, 1920, 1500)).resize((1280, 720), Image.LANCZOS)

pad, hdr = 26, 120
W = max(crop.width + 2 * pad, wide.width + 2 * pad)
H = hdr + 900 + 60 + 720 + pad
sheet = Image.new('RGB', (W, H), (14, 15, 20))
d = ImageDraw.Draw(sheet)
d.text((pad, 18), 'P0 · МАКРО гравировки на ребре значка — «%s»' % RIB_TEXT,
       font=ImageFont.truetype(GOTH, 32), fill=(226, 186, 104))
d.text((pad, 60), 'В клипе ребро мелькает «наездом» в паузе (0.35 с): знак поворачивается, '
                  'ребро крупно → гравировка прочитывается. Иначе (в общем плане) она микроскопическая.',
       font=ImageFont.truetype(LATO_B, 21), fill=(206, 211, 230))
d.text((pad, 88), 'Ниже: как ребро выглядит в кадре 16:9 БЕЗ наезда (справа-снизу) — гравировки не видно — '
                  'поэтому нужен крупный план.',
       font=ImageFont.truetype(LATO_B, 21), fill=(200, 150, 120))

y = hdr
sheet.paste(crop, (pad, y))
d.rectangle([pad, y, pad + crop.width, y + crop.height], outline=(80, 82, 96))
d.text((pad + crop.width + 16, y + 20), 'РЕБРО 90°', font=ImageFont.truetype(LATO_B, 24), fill=(150, 205, 150))
d.text((pad + crop.width + 16, y + 52), '«%s»' % RIB_TEXT, font=ImageFont.truetype(GOTH, 40), fill=(238, 214, 150))

y += 900 + 30
td = ImageDraw.Draw(wide)
td.rectangle([0, 0, wide.width - 1, wide.height - 1], outline=(90, 92, 106))
sheet.paste(wide, (pad, y))
sheet.save(OUT)
print('saved', os.path.relpath(OUT, HERE), sheet.size)
