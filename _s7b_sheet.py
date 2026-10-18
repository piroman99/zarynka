import os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import _s7_plaque

FIN = 'assets/final/prolog/s7.png'
subprocess.run(['/usr/bin/python3', '_prolog_finals.py', 's7'], check=True)

im = Image.open(FIN).convert('RGB')
W, H = im.size
s = W / 2400.0
bx = _s7_plaque.BOX
x0, y0, x1, y1 = [int(round(v * s)) for v in bx]
a = np.asarray(im.convert('L')).astype(np.float32)
reg = a[y0:y1, x0:x1]
print('BOX', bx, '-> final', (x0, y0, x1, y1), 'lum %.0f..%.0f mean %.0f' % (reg.min(), reg.max(), reg.mean()))
for yy in range(reg.shape[0]):
    line = ''
    for xx in range(reg.shape[1]):
        v = reg[yy, xx]
        line += '#' if v < 100 else '+' if v < 140 else '-' if v < 175 else '=' if v < 205 else '.'
    print(line)

pad = 16
full = im.resize((1200, round(H * 1200 / W)), Image.LANCZOS)
crop = im.crop((0, max(0, y0 - 34), 250, min(H, y1 + 34)))
crop = crop.resize((crop.width * 4, crop.height * 4), Image.LANCZOS)
sheet = Image.new('RGB', (max(full.width, crop.width) + 2 * pad, full.height + crop.height + 3 * pad),
                  (22, 22, 26))
sheet.paste(full, (pad, pad))
sheet.paste(crop, (pad, full.height + 2 * pad))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
d.text((pad, full.height + pad - 6), 'кроп 4x — табличка на стене слева', fill=(230, 230, 230), font=f)
sheet.save('assets/review/review_130_s7b_plaque.png')
print('sheet', sheet.size, os.path.getsize('assets/review/review_130_s7b_plaque.png'))
