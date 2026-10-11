# -*- coding: utf-8 -*-
"""Контрольный лист полного черновика К2b (7.4 с) + макро ребра."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '_intro_k2b.py')).read().split("if '--sheet' in sys.argv:")[0]
ns = {'__file__': os.path.join(HERE, '_intro_k2b.py'), '__name__': 'k2bmod'}
exec(compile(src, '_intro_k2b.py', 'exec'), ns)
render, REVIEW = ns['render'], ns['REVIEW']
from PIL import Image, ImageDraw, ImageFont
LATO = '/usr/share/fonts/truetype/lato/Lato-Medium.ttf'

T = [0.4, 1.2, 1.9, 2.25, 2.6, 3.0, 3.6, 4.4, 5.2, 6.6]
cols, rows = 5, 2
cw, ch = 480, 270
sheet = Image.new('RGB', (cols * cw + 20 * (cols + 1), rows * ch + 20 * (rows + 1) + 46), (16, 16, 20))
d = ImageDraw.Draw(sheet)
d.text((24, 12), 'К2b — усложнённый черновик (ребро + гравировка-пасхалка)', font=ImageFont.truetype(LATO, 24), fill=(255, 190, 120))
for i, tt in enumerate(T):
    fr = render(int(tt * 25)).resize((cw, ch), Image.LANCZOS)
    x = 20 + (i % cols) * (cw + 20); y = 46 + 20 + (i // cols) * (ch + 20)
    sheet.paste(fr, (x, y))
    ImageDraw.Draw(sheet).text((x + 8, y + 6), '%.2f c' % tt, font=ImageFont.truetype(LATO, 22), fill=(255, 220, 120))
sheet.save(os.path.join(REVIEW, 'review_38_k2b_full.png'))
print('лист:', os.path.relpath(os.path.join(REVIEW, 'review_38_k2b_full.png'), HERE), sheet.size)

# макро ребра в момент гравировки
for tt in (2.30, 2.55):
    fr = render(int(tt * 25)).crop((640, 60, 1280, 1020))
    out = os.path.join(REVIEW, 'review_39_rib_%.2f.png' % tt)
    fr.save(out); print('макро', os.path.relpath(out, HERE), fr.size)
