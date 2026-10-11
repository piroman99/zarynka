# -*- coding: utf-8 -*-
"""Меню пасхалок-гравировок на РЕБРЕ значка (для выбора заказчика).

Каждый вариант: золотое ребро (торец пятиугольника) с выштампованной надписью —
как на настоящих советских значках (цена, знак изготовителя, номер).
"""
import os, math
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'assets', 'review', 'review_35_rib_eggs.png')
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO = '/usr/share/fonts/truetype/lato/Lato-Medium.ttf'
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'

GOLD_D = (150, 116, 52)
GOLD = (214, 176, 96)
GOLD_L = (246, 226, 164)

# варианты надписей на ребре
VARIANTS = [
    ('A', 'ЛУНЦВЕТМЕТ · Ц. 67 КОП.', 'шутка-перевёртыш от «Вторцветмет» + цена значка; 67 = наш мем'),
    ('B', 'ЛУНЦВЕТМЕТ · ПАРТИЯ 2061', 'то же + год вселенной «СССР-2061»'),
    ('C', 'ЗНАК СССР-2061 · Ц. 67 КОП.', 'без шутки, чистый ретро-штамп (безопасный)'),
    ('D', '№ 12-04-1961 · Ц. 67 КОП.', 'серийный номер = дата полёта Гагарина (12.04.1961)'),
    ('E', 'ЛМД · Ц. 67 КОП.', '«Лунный монетный двор» (от ЛМД — Ленинградский) + цена'),
    ('F', 'МАРС — ДЕЛО ОБЩЕЕ! · 67 КОП.', 'лозунг из рассказа + six-seven'),
]


def font(sz, bold=False):
    return ImageFont.truetype(LATO_B if bold else LATO, sz)


def gold_bar(w, h, rng_seed=3):
    """Золотая полоса-торец с вертикальным градиентом (блик по металлу)."""
    import numpy as np
    yy = np.linspace(0, 1, h)[:, None]
    # объём металла: тёмно-светло-тёмно
    prof = 0.55 + 0.45 * np.sin(np.pi * yy)
    col = np.array(GOLD_L, float)[None, None, :]
    dark = np.array(GOLD_D, float)[None, None, :]
    img = dark + (col - dark) * prof[:, :, None]
    img = np.tile(img, (1, w, 1)).astype(np.uint8)
    return Image.fromarray(img, 'RGB')


def engrave(base, text, x, y, sz):
    """Выштамповать текст: тёмные буквы + светлая кромка снизу (объём)."""
    d = ImageDraw.Draw(base)
    f = font(sz, bold=True)
    w = d.textlength(text, font=f)
    d.text((x + 1, y + 2), text, font=f, fill=(255, 246, 220))     # блик кромки
    d.text((x, y), text, font=f, fill=(92, 66, 26))                 # тёмная гравировка
    return w


W = 1500
rows = len(VARIANTS)
BH = 96
GAP = 26
H = 120 + rows * (BH + GAP)
sheet = Image.new('RGB', (W, H), (18, 18, 22))
d = ImageDraw.Draw(sheet)
d.text((36, 26), 'Пасхалка в РЕБРО значка — варианты гравировки', font=ImageFont.truetype(GOTHIC, 34),
       fill=(255, 130, 120))
d.text((36, 72), 'ребро = торец пятиугольника (золото); надпись как штамп на советском значке',
       font=font(20), fill=(165, 165, 175))

for i, (tag, txt, note) in enumerate(VARIANTS):
    y = 120 + i * (BH + GAP)
    bar = gold_bar(W - 300, BH)
    engrave(bar, txt, 26, (BH - 52) // 2, 52)
    sheet.paste(bar, (36, y))
    d.text((44, y + BH + 2), f'{tag}.  {note}', font=font(18), fill=(190, 200, 215))

sheet.save(OUT)
print('saved', OUT, sheet.size)
