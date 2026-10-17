# -*- coding: utf-8 -*-
"""Лист-доказательство review_108: мобильный титул и игровой экран до/после."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, '.tmp_mob')
OUT = os.path.join(HERE, 'assets', 'review', 'review_108_mobile_fix.png')

ROWS = [
    ('Титул · портрет 390x844', [
        ('before_port_title.png', 'БЫЛО: «Тизер» ниже экрана'),
        ('after_port_title.png', 'СТАЛО: всё в кадре'),
        ('after_port_cinema.png', 'СТАЛО: тизер на весь экран'),
    ]),
    ('Игра · портрет 390x844 (S1)', [
        ('before_port_s1.png', 'БЫЛО: арт-полоска 219 px'),
        ('after_port_s1.png', 'СТАЛО: текст под артом'),
    ]),
    ('Титул · ландшафт 844x390', [
        ('before_land_title.png', 'БЫЛО: «Тизер» под срезом'),
        ('after_land_title.png', 'СТАЛО: блок вписан'),
    ]),
    ('Игра · ландшафт 844x390 (S1)', [
        ('before_land_s1.png', 'БЫЛО'),
        ('after_land_s1.png', 'СТАЛО'),
    ]),
]

H = 560          # высота картинки в листе
PAD = 18
CAP = 26
HEAD = 34
BG = (16, 18, 24)
FG = (232, 236, 245)
DIM = (150, 160, 175)


def font(sz):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
              '/usr/share/fonts/TTF/DejaVuSans.ttf',
              '/usr/share/fonts/dejavu/DejaVuSans.ttf'):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


F_HEAD = font(22)
F_CAP = font(17)
F_ROW = font(19)

# подготовка блоков
row_imgs = []
for title, items in ROWS:
    cells = []
    for fn, cap in items:
        im = Image.open(os.path.join(T, fn)).convert('RGB')
        k = H / im.height
        im = im.resize((max(1, int(im.width * k)), H), Image.LANCZOS)
        cells.append((im, cap))
    row_imgs.append((title, cells))

W = PAD
for _, cells in row_imgs:
    W = max(W, PAD + sum(c[0].width + PAD for c in cells))
HGT = PAD + HEAD
for title, cells in row_imgs:
    HGT += 26 + H + 26 + PAD

sheet = Image.new('RGB', (W, HGT), BG)
d = ImageDraw.Draw(sheet)
y = PAD

d.text((PAD, y), 'Зарянка vn2 — мобильная вёрстка: до / после (реальные рендеры Chromium)', font=F_HEAD, fill=FG)
y += HEAD

for title, cells in row_imgs:
    d.text((PAD, y), title, font=F_ROW, fill=(240, 150, 140))
    y += 26
    x = PAD
    for im, cap in cells:
        sheet.paste(im, (x, y))
        d.text((x + 2, y + im.height + 4), cap, font=F_CAP, fill=DIM)
        x += im.width + PAD
    y += H + 26 + PAD

sheet.save(OUT)
print(os.path.relpath(OUT, HERE), sheet.size, os.path.getsize(OUT), 'B')
