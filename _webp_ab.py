# -*- coding: utf-8 -*-
"""A/B 1:1: PNG-мастер против WebP q92 на самых сложных местах.
S1 — зерно плёнки и мел (детали в тенях), S5 — градиент неба и плакаты (риск бандинга).
Кропы 1:1 без масштабирования, слева PNG, справа WebP, по центру разделитель.
"""
import os, io
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
VN = os.path.join(HERE, 'vn2')
REV = os.path.join(HERE, 'assets', 'review')
LATO = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
Q = 92

CROPS = [
    ('s1', 'S1 · подворотня: зерно и мел в тенях', (700, 380)),
    ('s5', 'S5 · небо и плакаты: градиент, риск бандинга', (700, 120)),
]
CW, CH = 560, 340


def load_webp(img, q):
    b = io.BytesIO()
    img.save(b, 'WEBP', quality=q, method=6)
    b.seek(0)
    return Image.open(b).convert('RGB'), b.tell()


tiles = []
report = []
for name, cap, (x, y) in CROPS:
    png_path = os.path.join(VN, 'img', 'prolog', name + '.png')
    src = Image.open(png_path).convert('RGB')
    webp_im, wlen = load_webp(src, Q)
    box = (x, y, x + CW, y + CH)
    a = src.crop(box)
    b = webp_im.crop(box)
    # честная разница (усиленная ×8): где именно теряется
    from PIL import ImageChops
    diff = ImageChops.difference(a, b).point(lambda v: min(255, v * 8))
    report.append((name, os.path.getsize(png_path), wlen, diff))

    head = Image.new('RGB', (CW * 2 + 8, 40), (16, 16, 18))
    d = ImageDraw.Draw(head)
    f = ImageFont.truetype(LATO, 22)
    d.text((10, 9), 'PNG (мастер)', font=f, fill=(240, 228, 200))
    d.text((CW + 18, 9), 'WebP q%d' % Q, font=f, fill=(240, 228, 200))
    row = Image.new('RGB', (CW * 2 + 8, CH), (16, 16, 18))
    row.paste(a, (0, 0)); row.paste(b, (CW + 8, 0))

    head2 = Image.new('RGB', (CW * 2 + 8, 36), (16, 16, 18))
    ImageDraw.Draw(head2).text((10, 7), 'разница ×8', font=ImageFont.truetype(LATO, 18), fill=(200, 200, 200))
    row2 = Image.new('RGB', (CW * 2 + 8, CH), (16, 16, 18))
    row2.paste(diff, (0, 0)); row2.paste(diff, (CW + 8, 0))

    capbar = Image.new('RGB', (CW * 2 + 8, 34), (10, 10, 12))
    ImageDraw.Draw(capbar).text((10, 7), cap, font=ImageFont.truetype(LATO, 20), fill=(226, 186, 104))

    t = Image.new('RGB', (CW * 2 + 8, 40 + CH + 36 + 34), (16, 16, 18))
    t.paste(capbar, (0, 0)); t.paste(head, (0, 34)); t.paste(row, (0, 74))
    t.paste(head2, (0, 74 + CH)); t.paste(row2, (0, 74 + CH + 36))
    tiles.append(t)

TH = sum(t.size[1] for t in tiles) + 16 * (len(tiles) - 1)
sheet = Image.new('RGB', (CW * 2 + 8, TH), (8, 8, 10))
y = 0
for t in tiles:
    sheet.paste(t, (0, y)); y += t.size[1] + 16

out = os.path.join(REV, 'review_100_webp_ab.png')
sheet.save(out)
print('лист ->', os.path.relpath(out, HERE), sheet.size, os.path.getsize(out), 'B')
for name, plen, wlen, diff in report:
    import numpy as np
    d = np.asarray(diff, np.float32)
    print('%s: png %.0f KB -> webp q%d %.0f KB (%.1f×) | MAE разницы %.2f, макс %d'
          % (name, plen / 1024, Q, wlen / 1024, plen / wlen, d.mean() / 8, d.max() / 8))
