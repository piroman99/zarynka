# -*- coding: utf-8 -*-
"""Лист-сравнение всех вариантов Сергея -> assets/review/review_71_sergey_variants.png"""
import os
from PIL import Image, ImageDraw
H = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(H, 'assets', 'gen')
S = os.path.join(H, 'assets', 'sprites')
REV = os.path.join(H, 'assets', 'review')
cands = [
    ('sergey_eng_0\n(использован)', os.path.join(G, 'sergey_eng_0.png')),
    ('sergey_0.png', os.path.join(G, 'sergey_0.png')),
    ('sergey_0.jpg', os.path.join(G, 'sergey_0.jpg')),
    ('sergey_grok_0', os.path.join(G, 'sergey_grok_0.jpg')),
    ('sprites/sergey.png\n(старый)', os.path.join(S, 'sergey.png')),
    ('eng_old__flux-2', os.path.join(G, 'sergey_eng_old__flux-2_0.jpg')),
    ('eng_old__gpt-image-2', os.path.join(G, 'sergey_eng_old__gpt-image-2_0.png')),
    ('eng_old__grok', os.path.join(G, 'sergey_eng_old__grok-imagine_0.jpg')),
    ('eng_old__nano-banana-2', os.path.join(G, 'sergey_eng_old__nano-banana-2_0.jpg')),
]
cw, ch = 320, 420
cols = 3
rows = (len(cands) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cw, rows * ch), (14, 16, 22))
d = ImageDraw.Draw(sheet)
for i, (lbl, p) in enumerate(cands):
    x, y = (i % cols) * cw, (i // cols) * ch
    if os.path.exists(p):
        im = Image.open(p).convert('RGB')
        im.thumbnail((cw - 8, ch - 34), Image.LANCZOS)
        sheet.paste(im, (x + 4, y + 30))
    d.text((x + 6, y + 6), lbl, fill=(255, 235, 230))
    d.rectangle([x, y, x + cw - 1, y + ch - 1], outline=(50, 54, 68))
sheet.save(os.path.join(REV, 'review_71_sergey_variants.png'))
print('->', sheet.size)
