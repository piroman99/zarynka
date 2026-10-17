# -*- coding: utf-8 -*-
"""4 кандидата посадки табло на будке + кропы. Ищем место, где панель читается КАК ЖЕЛЕЗО,
а не наклейка поверх стекла: под козырьком, на стойке рамы, на глухой панели, у турникета."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
import _s6_clock_ab as C

plate = Image.open(os.path.join(HERE, 'assets', 'gen', 's6_gpt3_b_0.png')).convert('RGB')
plate = plate.resize((2400, 1350), Image.LANCZOS)

CANDS = [
    ('D1 · под козырьком будки',      (1846, 246, 2120, 330)),
    ('D2 · на левой стойке рамы',     (1806, 300, 1886, 470)),
    ('D3 · на глухой панели снизу',   (1852, 500, 2126, 584)),
    ('D4 · на стойке ворот справа',   (2216, 300, 2320, 384)),
]

f = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Bold.ttf', 20)
crops = []
for label, box in CANDS:
    v = C.clock(plate.copy(), box)
    pad = 70
    c = v.crop((max(0, box[0] - pad), max(0, box[1] - pad),
                min(2400, box[2] + pad), min(1350, box[3] + pad)))
    c = c.resize((c.width * 2, c.height * 2), Image.LANCZOS)
    crops.append((label, c))
    print(label, box)

W = 1320
pad, lab = 18, 30
H = 8 + sum(lab + c.height + pad for _, c in crops)
sheet = Image.new('RGB', (W + 2 * pad, H), (18, 20, 26))
d = ImageDraw.Draw(sheet)
y = 8
for label, c in crops:
    d.text((pad, y), label, font=f, fill=(232, 200, 140)); y += lab
    cc = c.resize((W, int(c.height * W / c.width)), Image.LANCZOS) if c.width > W else c
    sheet.paste(cc, (pad, y)); y += cc.height + pad
p = os.path.join(HERE, 'assets', 'review', 'review_123_s6_clock_place.png')
sheet.save(p)
print('sheet ->', os.path.relpath(p, HERE), sheet.size)
