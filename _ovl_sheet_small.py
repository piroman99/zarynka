# -*- coding: utf-8 -*-
"""Компактный лист кадров 9-12 для показа: 5 страниц в 2 колонки."""
import os, glob
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(HERE, '.tmp_vo')
OUT = os.path.join(HERE, '_sat', 'ovl_sheet_small.jpg')
ITEMS = [('s3', 0, 'кадр 9 · зал'), ('s4', 0, 'кадр 10 · ролик'),
         ('s5a', 0, 'кадр 11 · лозунг (стр.1)'), ('s5a', 1, 'кадр 11 · лозунг (стр.2)'),
         ('s5b', 0, 'кадр 12 · Совет')]
CW, PAD, LAB = 700, 12, 24
CH = int(round(CW * 720 / 1280))
COLS = 2
rows = (len(ITEMS) + COLS - 1) // COLS
W = COLS * CW + (COLS + 1) * PAD
H = rows * (CH + LAB + PAD) + PAD
cv = Image.new('RGB', (W, H), (14, 16, 22))
d = ImageDraw.Draw(cv)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
for i, (nid, p, lab) in enumerate(ITEMS):
    src = os.path.join(TMP, 'pc_%s_%d_on.png' % (nid, p))
    if not os.path.exists(src):
        src = os.path.join(TMP, 'ovl_%s_%d.png' % (nid, p))
    im = Image.open(src).convert('RGB').resize((CW, CH), Image.LANCZOS)
    x = PAD + (i % COLS) * (CW + PAD)
    y = PAD + (i // COLS) * (CH + LAB + PAD)
    cv.paste(im, (x, y))
    d.rectangle([x, y, x + CW - 1, y + CH - 1], outline=(52, 56, 68))
    d.text((x, y + CH + 3), lab, fill=(214, 218, 226), font=f)
cv.save(OUT, quality=88)
print('saved', OUT, cv.size, os.path.getsize(OUT))
