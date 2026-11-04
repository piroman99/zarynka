# -*- coding: utf-8 -*-
"""A/B вырезания волос: старая вырезка (cutout сборки) против новой (мягкая альфа).

Кроп головы и плеч в 2× на тёмно-синем фоне игры — на нём серая кайма и серые пятна
в петлях волос видны сразу. Плюс кроп головы поэта из ЖИВОГО кадра игры.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _poet_hair_check import cutout_old  # noqa: E402

GEN = os.path.join(HERE, 'assets', 'gen')
SPR = os.path.join(HERE, 'assets', 'sprites')
REV = os.path.join(HERE, 'assets', 'review')
SAT = os.path.join(HERE, '_sat')
os.makedirs(SAT, exist_ok=True)

BGCOL = (34, 40, 56)          # тёмно-синий, как интерьер приёмной в игре


def flat(im_rgba, size=None):
    canvas = Image.new('RGB', im_rgba.size, BGCOL)
    canvas.paste(im_rgba, (0, 0), im_rgba)
    return canvas


def head_crop(im, frac=0.46):
    """Верхняя часть спрайта (голова и плечи) — там, где волосы."""
    w, h = im.size
    return im.crop((0, 0, w, int(h * frac)))


def up2(im):
    return im.resize((im.width * 2, im.height * 2), Image.LANCZOS)


panels = []

# 1) старое вырезание из сырого кадра
raw = os.path.join(GEN, 'poet2_b_0.png')
rgb_o, a_o = cutout_old(Image.open(raw))
old_rgba = Image.fromarray(np.dstack([rgb_o, a_o * 255]).astype(np.uint8), 'RGBA')
panels.append((up2(head_crop(flat(old_rgba))), 'БЫЛО: cutout сборки (flood-fill)'))

# 2) новое матирование
new = Image.open(os.path.join(SPR, 'poet_ha_neutral.png')).convert('RGBA')
panels.append((up2(head_crop(flat(new))), 'СТАЛО: мягкая альфа + петли + despill'))

# 3) кроп из живого кадра игры
live = os.path.join(REV, 'review_134_poet_p0.png')
if os.path.exists(live):
    im = Image.open(live).convert('RGB')
    # спрайт поэта в 1600x900: left 855, width 509, height 749, bottom 780
    box = (855, 20, 855 + 509, 20 + int(749 * 0.42))
    c = im.crop(box)
    panels.append((c.resize((c.width * 2, c.height * 2), Image.LANCZOS),
                   'В ИГРЕ: приёмная, стр. 0 (×2)'))

pad, cap = 10, 26
H = max(p[0].height for p in panels) + cap + pad * 2
W = sum(p[0].width for p in panels) + pad * (len(panels) + 1)
sheet = Image.new('RGB', (W, H), (16, 16, 20))
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
except Exception:
    font = ImageFont.load_default()
x = pad
for im, label in panels:
    sheet.paste(im, (x, pad))
    d.text((x + 3, pad + im.height + 4), label, fill=(235, 225, 205), font=font)
    x += im.width + pad
out = os.path.join(SAT, 'sheet_poet_hair_ab.png')
sheet.save(out)
print('sheet ->', os.path.relpath(out, HERE), os.path.getsize(out), 'B')
for im, label in panels:
    print('  %-40s %dx%d' % (label, im.width, im.height))
