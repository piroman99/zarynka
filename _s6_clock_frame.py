# -*- coding: utf-8 -*-
"""Варианты посадки табло по замеренной геометрии будки: лист + кропы в нативном разрешении."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
import _clock_led as L

plate = Image.open(os.path.join(HERE, 'assets', 'gen', 's6_gpt3_b_0.png')).convert('RGB')
plate = plate.resize((2400, 1350), Image.LANCZOS)

# стойки будки: 1839..2178, средняя связь y=397, низ y=598
CANDS = [
    ('F1 · на раме будки, над окном (x 1852..2166, y 306..392)', (1852, 306, 2166, 392)),
    ('F2 · на раме будки, ниже окна (y 500..586)',               (1852, 500, 2166, 586)),
    ('F3 · на правой стойке будки (x 2140..2320, y 330..405)',   (2140, 330, 2320, 405)),
]

f = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Bold.ttf', 20)
rows = []
for label, box in CANDS:
    v = L.clock(plate.copy(), box)
    pad = 60
    c = v.crop((max(0, box[0] - pad), max(0, box[1] - pad),
                min(2400, box[2] + pad), min(1350, box[3] + pad)))
    c = c.resize((c.width * 2, c.height * 2), Image.LANCZOS)
    rows.append((label, c))
    print(label, box)

W = 1320
pad, lab = 18, 30
imgs = [(lb, c if c.width <= W else c.resize((W, int(c.height * W / c.width)), Image.LANCZOS))
        for lb, c in rows]
H = 8 + sum(lab + im.height + pad for _, im in imgs)
sheet = Image.new('RGB', (W + 2 * pad, H), (18, 20, 26))
d = ImageDraw.Draw(sheet)
y = 8
for lb, im in imgs:
    d.text((pad, y), lb, font=f, fill=(232, 200, 140)); y += lab
    sheet.paste(im, (pad, y)); y += im.height + pad
p = os.path.join(HERE, 'assets', 'review', 'review_124_s6_clock_frame.png')
sheet.save(p)
print('sheet ->', os.path.relpath(p, HERE), sheet.size)
