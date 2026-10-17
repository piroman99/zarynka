# -*- coding: utf-8 -*-
"""Числовая сверка листа «до/после»: что реально изменилось на пикселях."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, '.tmp_mob')


def stats(fn, box=None):
    im = Image.open(os.path.join(T, fn)).convert('RGB')
    if box:
        im = im.crop(box)
    px = list(im.getdata())
    n = len(px)
    red = sum(1 for (r, g, b) in px if r > 140 and r > g + 40 and r > b + 40) / n
    bright = sum(1 for (r, g, b) in px if r + g + b > 540) / n
    dark = sum(1 for (r, g, b) in px if r + g + b < 60) / n
    return {'red': round(red, 4), 'bright': round(bright, 4), 'dark': round(dark, 4), 'size': im.size}


# портрет 390x844 @dpr2 → картинка 780x1688; кнопка «Тизер» была y544..588 CSS
TEASER = (0, 2 * 530, 780, 2 * 600)      # полоса, где должна быть кнопка «Тизер»
TEXTBAND = (0, 2 * 300, 780, 2 * 800)    # полоса ниже арта (219 CSS px)
print('== портрет, полоса кнопки «Тизер» (y 530..600 CSS) ==')
for tag in ('before', 'after'):
    print('  %-6s' % tag, stats('%s_port_title.png' % tag, TEASER))
print('== портрет, полоса под артом (y 300..800 CSS) ==')
for tag in ('before', 'after'):
    print('  %-6s' % tag, stats('%s_port_s1.png' % tag, TEXTBAND))
print('== портрет, весь экран игры ==')
for tag in ('before', 'after'):
    print('  %-6s' % tag, stats('%s_port_s1.png' % tag))
