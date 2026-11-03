# -*- coding: utf-8 -*-
"""Проверка кадров 9/10/12 без вожжённых надписей: полосы + кроп метки."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FIN = os.path.join(HERE, 'assets', 'final', 'prolog')
OUT = os.path.join(HERE, '_sat')
os.makedirs(OUT, exist_ok=True)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
fl = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)

items = [('s3', 'кадр 9 · зал (плашка и строки убраны → титр-слой)'),
         ('s4', 'кадр 10 · ролик (подпись с экрана снята, метка новая)'),
         ('s5', 'кадр 12 · Совет (полоса лозунга и чип сняты)')]
cw, pad, lab = 1000, 14, 26
ch = int(round(cw * 1080 / 1920))
W = cw + 2 * pad
H = sum(ch + lab + pad for _ in items) + pad
cv = Image.new('RGB', (W, H), (14, 16, 22))
d = ImageDraw.Draw(cv)
y = pad
for n, labt in items:
    im = Image.open(os.path.join(FIN, n + '.png')).convert('RGB').resize((cw, ch), Image.LANCZOS)
    cv.paste(im, (pad, y))
    d.rectangle([pad, y, pad + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((pad, y + ch + 3), labt, fill=(214, 218, 226), font=fl)
    y += ch + lab + pad
p = os.path.join(OUT, 'check_9_10_12.png')
cv.save(p)
print('saved', p, cv.size)

# кропы меток (левый верхний угол, натив 1920x1080 -> доля 520x120 в 2400-пространстве)
crops = []
for n, _ in items:
    im = Image.open(os.path.join(FIN, n + '.png')).convert('RGB')
    crops.append((n, im.crop((0, 0, 700, 160))))
W2 = max(c.size[0] for _, c in crops) + 2 * 12
H2 = sum(c.size[1] + 24 + 12 for _, c in crops) + 12
cv2 = Image.new('RGB', (W2, H2), (14, 16, 22))
d2 = ImageDraw.Draw(cv2)
y = 12
for n, c in crops:
    cv2.paste(c, (12, y))
    d2.text((12, y + c.size[1] + 3), n + ' · метка (натив)', fill=(214, 218, 226), font=fl)
    y += c.size[1] + 24 + 12
p2 = os.path.join(OUT, 'check_9_10_12_tags.png')
cv2.save(p2)
print('saved', p2, cv2.size)
