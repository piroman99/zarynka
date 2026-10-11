# -*- coding: utf-8 -*-
"""Лист ключевых кадров вращательного черновика (16:9)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '_znak3d_rot.py')).read()
src = src.split("if '--frames' in sys.argv:")[0]
ns = {'__file__': os.path.join(HERE, '_znak3d_rot.py'), '__name__': 'rotmod'}
exec(compile(src, '_znak3d_rot.py', 'exec'), ns)
render, REVIEW = ns['render'], ns['REVIEW']
from PIL import Image, ImageDraw, ImageFont
LATO = '/usr/share/fonts/truetype/lato/Lato-Medium.ttf'
T = [0.0, 1.0, 1.7, 2.2, 3.0, 3.8, 5.0, 5.3]
cw, ch = 480, 270
cols, rows = 4, 2
sheet = Image.new('RGB', (cols * cw + 20 * (cols + 1), rows * ch + 20 * (rows + 1) + 50), (14, 14, 18))
d = ImageDraw.Draw(sheet)
d.text((22, 12), '3D-значок: вращение черновик (ребро появляется само, силуэт по пятиугольнику)',
       font=ImageFont.truetype(LATO, 24), fill=(255, 190, 120))
for i, tt in enumerate(T):
    fr = render(tt).resize((cw, ch), Image.LANCZOS)
    x = 20 + (i % cols) * (cw + 20); y = 50 + 20 + (i // cols) * (ch + 20)
    sheet.paste(fr, (x, y))
    ImageDraw.Draw(sheet).text((x + 8, y + 6), '%.1f c · %d°' % (tt, round(ns['angle_at'](tt))),
                               font=ImageFont.truetype(LATO, 22), fill=(255, 220, 120))
out = os.path.join(REVIEW, 'review_50_znak3d_rot_sheet.png')
sheet.save(out)
print('saved', os.path.relpath(out, HERE), sheet.size)
