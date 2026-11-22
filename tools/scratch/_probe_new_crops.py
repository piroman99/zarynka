# -*- coding: utf-8 -*-
"""Нативные кропы новых кадров для проверки БУКВ глазами (+ лист с полосами).

    python3 _probe_new_crops.py

Делает:
  _sat/crop_s1wall_a_mid.png / _b_mid.png   — широкая полоса кадра 1:1 (стена с граффити)
  _sat/crop_p6luna_a_mid.png / _b_mid.png   — полоса базы 1:1
  _sat/sheet_s1wall_p6luna_big.png          — лист 2x2: s1wall A/B, p6luna A/B
"""
import os
from PIL import Image, ImageDraw, ImageFont

GEN = 'assets/gen'
SAT = '_sat'
os.makedirs(SAT, exist_ok=True)

BANDS = [('s1wall_a', 's1wall_a__gpt-image-2_0.png', (0.0, 0.28, 1.0, 0.88)),
         ('s1wall_b', 's1wall_b__gpt-image-2_0.png', (0.0, 0.28, 1.0, 0.88)),
         ('p6luna_a', 'p6luna_a__gpt-image-2_0.jpg', (0.0, 0.10, 1.0, 0.85)),
         ('p6luna_b', 'p6luna_b__gpt-image-2_0.png', (0.0, 0.10, 1.0, 0.85))]


def font(sz):
    for p in ('/usr/share/fonts/truetype/lato/Lato-Medium.ttf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def main():
    tiles = []
    for name, fn, box in BANDS:
        im = Image.open(os.path.join(GEN, fn)).convert('RGB')
        w, h = im.size
        c = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
        cp = os.path.join(SAT, 'crop_%s_mid.png' % name)
        c.save(cp)
        print('%-9s кроп 1:1 %dx%d -> %s' % (name, c.width, c.height, cp))
        tiles.append((name, im))

    W = 1200
    rows = []
    for name, im in tiles:
        h = round(im.height * W / im.width)
        rows.append((name, im.resize((W, h), Image.LANCZOS), h))
    H = sum(r[2] + 34 for r in rows) + 8
    out = Image.new('RGB', (W, H), (16, 16, 18))
    d = ImageDraw.Draw(out)
    f = font(24)
    y = 4
    for name, im, h in rows:
        d.text((12, y + 2), name, font=f, fill=(240, 222, 180))
        y += 32
        out.paste(im, (0, y))
        y += h + 2
    p = os.path.join(SAT, 'sheet_s1wall_p6luna_big.png')
    out.save(p)
    print('лист ->', p)


if __name__ == '__main__':
    main()
