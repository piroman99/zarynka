# -*- coding: utf-8 -*-
"""Свежая проверка кадров паузы на ребре (ЛМД)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '_intro_k2b.py')).read().split("if '--sheet' in sys.argv:")[0]
ns = {'__file__': os.path.join(HERE, '_intro_k2b.py'), '__name__': 'k2bmod'}
exec(compile(src, '_intro_k2b.py', 'exec'), ns)
render, REVIEW = ns['render'], ns['REVIEW']
from PIL import Image, ImageDraw, ImageFont
LATO = '/usr/share/fonts/truetype/lato/Lato-Medium.ttf'

# 1) три полных кадра (960x540) сверху
T = [2.10, 2.35, 2.60]
cw, ch = 960, 540
top = Image.new('RGB', (cw, ch * 3 + 20 * 4), (16, 16, 20))
for i, tt in enumerate(T):
    fr = render(int(tt * 25)).resize((cw, ch), Image.LANCZOS)
    top.paste(fr, (0, 20 + i * (ch + 20)))
    ImageDraw.Draw(top).text((12, 24 + i * (ch + 20)), '%.2f c' % tt,
                             font=ImageFont.truetype(LATO, 26), fill=(255, 220, 120))
top.save(os.path.join(REVIEW, 'review_40_pause_frames.png'))
print('saved review_40_pause_frames.png', top.size)

# 2) макро-кроп центра (ребро) из кадра 2.35
fr = render(int(2.35 * 25)).crop((600, 40, 1320, 1080))
fr.save(os.path.join(REVIEW, 'review_41_rib_macro.png'))
print('saved review_41_rib_macro.png', fr.size)
