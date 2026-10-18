# -*- coding: utf-8 -*-
"""Крупный зум лица (только лицо, 900px) — по одному листу на эмоцию."""
import os, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
V2 = os.path.join(GEN, '_sergey_v2')
REV = os.path.join(HERE, 'assets', 'review')

SETS = {
    'smile': [('base', os.path.join(GEN, 'sergey_eng_old__flux-2_0.jpg')),
              ('OLD', os.path.join(GEN, 'sergey_smile_0.jpg')),
              ('flux v2', os.path.join(V2, 'sergey_smile__flux-2_0.jpg')),
              ('gpt v2', os.path.join(V2, 'sergey_smile__gpt-image-2_0.png'))],
    'concerned': [('base', os.path.join(GEN, 'sergey_eng_old__flux-2_0.jpg')),
                  ('OLD', os.path.join(GEN, 'sergey_concerned_0.jpg')),
                  ('flux v2', os.path.join(V2, 'sergey_concerned__flux-2_0.jpg')),
                  ('gpt v2', os.path.join(V2, 'sergey_concerned__gpt-image-2_0.png'))],
}

which = sys.argv[1:] or list(SETS)
for key in which:
    tiles = []
    for label, p in SETS[key]:
        im = Image.open(p).convert('RGB')
        w, h = im.size
        box = (int(w * .22), int(h * .04), int(w * .78), int(h * .40))
        face = im.crop(box)
        tw = 760
        face = face.resize((tw, int(face.height * tw / face.width)), Image.LANCZOS)
        tiles.append((label, face))
    th = tiles[0][1].height
    sheet = Image.new('RGB', (tw * len(tiles), th + 26), (12, 14, 20))
    d = ImageDraw.Draw(sheet)
    for i, (label, im) in enumerate(tiles):
        sheet.paste(im, (i * tw, 26))
        d.text((i * tw + 8, 8), label, fill=(255, 255, 255))
    p = os.path.join(REV, 'review_74_sergey_%s_zoom.png' % key)
    sheet.save(p)
    print(p, sheet.size)
