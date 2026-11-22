# -*- coding: utf-8 -*-
"""Лист выбора Сергея: партия «постарше» (42) + текущий (33). -> review_72_sergey_choice.png"""
import os
from PIL import Image, ImageDraw, ImageFont
H = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(H, 'assets', 'gen')
REV = os.path.join(H, 'assets', 'review')
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def font(s):
    return ImageFont.truetype(F, s) if os.path.exists(F) else ImageFont.load_default()


cands = [
    ('СЕЙЧАС в VN: sergey_eng_0 (33 года)', os.path.join(G, 'sergey_eng_0.png')),
    ('flux-2  (3.38₽)  «42»', os.path.join(G, 'sergey_eng_old__flux-2_0.jpg')),
    ('gpt-image-2  (4.06₽)', os.path.join(G, 'sergey_eng_old__gpt-image-2_0.png')),
    ('nano-banana-2  (5.42₽)', os.path.join(G, 'sergey_eng_old__nano-banana-2_0.jpg')),
    ('grok-imagine  (2.51₽)', os.path.join(G, 'sergey_eng_old__grok-imagine_0.jpg')),
]
cw, ch = 470, 640
cols = 3
rows = (len(cands) + cols - 1) // cols
W = cols * cw + (cols + 1) * 12
Hh = 44 + rows * (ch + 40) + 12
sheet = Image.new('RGB', (W, Hh), (18, 20, 26))
d = ImageDraw.Draw(sheet)
d.text((16, 12), 'Сергей Лихнецкий — партия «постарше» (42): выбор движка',
       fill=(240, 240, 245), font=font(24))
for i, (lbl, p) in enumerate(cands):
    r, c = divmod(i, cols)
    x = 12 + c * (cw + 12)
    y = 52 + r * (ch + 40)
    d.rectangle([x, y, x + cw, y + ch], fill=(30, 33, 40))
    if os.path.exists(p):
        im = Image.open(p).convert('RGB')
        im.thumbnail((cw - 10, ch - 10), Image.LANCZOS)
        sheet.paste(im, (x + (cw - im.width) // 2, y + (ch - im.height) // 2))
    d.text((x + 4, y + ch + 8), lbl, fill=(255, 220, 214), font=font(19))
    d.rectangle([x, y, x + cw, y + ch], outline=(56, 60, 74))
out = os.path.join(REV, 'review_72_sergey_choice.png')
sheet.save(out)
print('->', sheet.size)
