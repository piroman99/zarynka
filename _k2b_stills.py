# -*- coding: utf-8 -*-
"""Стоп-кадры момента «ЛМД» на ребре: полный кадр + макро торец."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '_intro_k2b.py')).read().split("if '--sheet' in sys.argv:")[0]
ns = {'__file__': os.path.join(HERE, '_intro_k2b.py'), '__name__': 'k2bmod'}
exec(compile(src, '_intro_k2b.py', 'exec'), ns)
render, REVIEW = ns['render'], ns['REVIEW']
from PIL import Image, ImageDraw, ImageFont
LATO = '/usr/share/fonts/truetype/lato/Lato-Medium.ttf'
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'


def caption(img, txt):
    im = img.copy().convert('RGB')
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, im.width, 46], fill=(14, 14, 18))
    d.text((16, 10), txt, font=ImageFont.truetype(LATO, 26), fill=(255, 205, 120))
    return im


# --- макро торца (кадр 2.45 с): вырез колонки ребра и увеличение ---
fr = render(int(2.45 * 25))
col = fr.crop((900, 60, 1080, 1020))                 # узкая колонка вдоль ребра
col = col.resize((col.width * 2, col.height * 2), Image.LANCZOS)
col = caption(col, 'ребро значка · гравировка «ЛМД · Ц. 67 КОП.» (макро)')
col.save(os.path.join(REVIEW, 'review_43_rib_lmd_macro.png'))
print('saved review_43_rib_lmd_macro.png', col.size)

# --- полный кадр паузы (2.45 с) ---
full = render(int(2.45 * 25)).resize((1280, 720), Image.LANCZOS)
caption(full, '2.45 c — пауза на ребре').save(os.path.join(REVIEW, 'review_44_rib_lmd_pause.png'))
print('saved review_44_rib_lmd_pause.png')

# --- два кадра: наезд на ребро и уход на оборот ---
a = render(int(2.30 * 25)).resize((640, 360), Image.LANCZOS)
b = render(int(2.90 * 25)).resize((640, 360), Image.LANCZOS)
sh = Image.new('RGB', (640 * 2 + 60, 360 + 90), (16, 16, 20))
d = ImageDraw.Draw(sh)
d.text((20, 16), 'К2b · ребро с гравировкой «ЛМД · Ц. 67 КОП.»', font=ImageFont.truetype(GOTHIC, 30), fill=(255, 130, 120))
sh.paste(caption(a, '2.30 c · наезд на торец'), (20, 60))
sh.paste(caption(b, '2.90 c · докрут на оборот'), (640 + 40, 60))
sh.save(os.path.join(REVIEW, 'review_45_rib_lmd_pair.png'))
print('saved review_45_rib_lmd_pair.png', sh.size)
