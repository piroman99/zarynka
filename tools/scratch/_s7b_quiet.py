import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import _s7_plaque2 as P

base = Image.open('assets/gen/s7b_gpt_a_0.png').convert('RGB').resize((2400, 1350), Image.LANCZOS)
a = np.asarray(base).astype(np.float32)
print('wall RGB:', np.round(a[350:430, 20:90].reshape(-1, 3).mean(0)).astype(int))

items = [('none', 'без таблички'), ('a', 'A · небольшая, в тон стене'),
         ('b', 'B · ещё мельче, одна строка'), ('c', 'C · прежний размер, без красного')]
crops = []
for key, label in items:
    im = base if key == 'none' else P.plaque(base, key)
    crops.append((im.crop((0, 300, 300, 480)).resize((600, 360), Image.LANCZOS), label))

pad, CW, CH = 10, 600, 360
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
sheet = Image.new('RGB', (2 * CW + 3 * pad, 2 * (CH + 30) + 3 * pad), (22, 22, 26))
d = ImageDraw.Draw(sheet)
for i, (c, label) in enumerate(crops):
    r, cc = divmod(i, 2)
    x, y = pad + cc * (CW + pad), pad + r * (CH + 30 + pad)
    sheet.paste(c, (x, y))
    d.text((x + 2, y + CH + 4), label, fill=(235, 235, 235), font=f)
sheet.save('assets/review/review_131_s7_plaque_quiet.png')
print('sheet', sheet.size, os.path.getsize('assets/review/review_131_s7_plaque_quiet.png'))

for key in ('a', 'b'):
    im = P.plaque(base, key)
    im.resize((1400, 788), Image.LANCZOS).save('assets/review/_full_%s.jpg' % key, quality=88)
    print(key, os.path.getsize('assets/review/_full_%s.jpg' % key))
