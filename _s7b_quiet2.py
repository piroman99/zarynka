import os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import _s7_plaque2 as P

FIN = 'assets/final/prolog/s7.png'
subprocess.run(['/usr/bin/python3', '_prolog_finals.py', 's7'], check=True)

im = Image.open(FIN).convert('RGB')
W, H = im.size
s = W / 2400.0
st = P.STYLES['a']
x0, y0, x1, y1 = [int(round(v * s)) for v in st['box']]
a = np.asarray(im).astype(np.float32)
reg = a[y0:y1, x0:x1]
wall = a[y0:y1, 0:max(1, x0 - 2)]
print('final', (W, H), 'box', (x0, y0, x1, y1), 'size', (x1 - x0, y1 - y0))
print('plate mean RGB %s   wall mean RGB %s   Δlum %.1f' % (
    np.round(reg.reshape(-1, 3).mean(0)).astype(int),
    np.round(wall.reshape(-1, 3).mean(0)).astype(int),
    reg.mean() - wall.mean()))

g = reg.mean(2)
for yy in range(g.shape[0]):
    print(''.join('#' if v < 118 else '+' if v < 136 else '-' if v < 152 else '=' if v < 168 else '.'
                  for v in g[yy]))

pad = 14
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 19)
# лист: полный кадр 1000 px + кроп 4x таблички
full = im.resize((1000, round(H * 1000 / W)), Image.LANCZOS)
crop = im.crop((0, max(0, y0 - 26), 210, min(H, y1 + 26)))
crop = crop.resize((crop.width * 4, crop.height * 4), Image.LANCZOS)
sheet = Image.new('RGB', (max(full.width, crop.width) + 2 * pad, full.height + crop.height + 3 * pad),
                  (22, 22, 26))
sheet.paste(full, (pad, pad))
sheet.paste(crop, (pad, full.height + 2 * pad))
ImageDraw.Draw(sheet).text((pad, full.height + pad - 4),
                           'кроп 4x — тихая табличка на стене', fill=(232, 232, 232), font=f)
sheet.save('assets/review/review_132_s7_plaque_quiet_vn.png')
print('sheet', sheet.size, os.path.getsize('assets/review/review_132_s7_plaque_quiet_vn.png'))
