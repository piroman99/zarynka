# -*- coding: utf-8 -*-
"""Скамейка-проп: из кадра `bench_long_0.png` сделать чистую RGBA-фигуру и найти сиденье.

Зачем свой шаг: акварель пришла с мягкой «плёнкой» (виньетка бумаги) по всему холсту —
матирование видит её как полупрозрачный фон (20% пикселей), и проп получился бы серым
прямоугольником поверх фона. Лечим: alpha' = clip((a-60)/(255-60)) — плёнка уходит,
дерево (плотная заливка) остаётся, потом лёгкое замыкание дыр и подрезка по bbox.

Печатает профиль по строкам в средней трети ширины — по нему видно, где просвет под
сиденьем (там меньше дерева), то есть где линия сиденья.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _poet_matte import matte  # noqa: E402

GEN = os.path.join(HERE, 'assets', 'gen')
SPR = os.path.join(HERE, 'assets', 'sprites')
A_LO, A_HI = 60.0, 210.0


def prep(name, keep_big=True):
    rgba, st = matte(Image.open(os.path.join(GEN, name + '_0.png')))
    a = np.asarray(rgba.split()[-1]).astype(np.float32)
    a = np.clip((a - A_LO) / (A_HI - A_LO), 0, 1)
    # плёнка отрезана, но в дереве остались дырки от светлых мазков — закрываем их:
    # маска «дерево» = a>0.35, затем max-фильтр 5 px, потом обратно умножаем мягкую альфу
    hard = Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))
    soft = Image.fromarray((a * 255).astype(np.uint8))
    a2 = np.minimum(np.asarray(soft, np.float32), np.asarray(hard, np.float32)) / 255.0
    a2 = np.where(a2 > 0.28, np.maximum(a2, 0.55), a2)      # плотное дерево не «худеет»
    a2 = Image.fromarray((a2 * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    out = rgba.copy()
    out.putalpha(a2)
    m = np.asarray(a2) > 150          # ПЛОТНОЕ дерево: по нему и режем в размер
    ys, xs = np.nonzero(m)
    pad = int(round(0.008 * (ys.max() - ys.min())))
    box = (max(0, xs.min() - pad), max(0, ys.min() - pad),
           min(rgba.width, xs.max() + pad), min(rgba.height, ys.max() + pad))
    crop = out.crop(box)
    # ПРАВЫЙ КРАЙ ГАСИМ В ПРОЗРАЧНОСТЬ: генератор обрезал скамейку краем кадра, и без
    # растушёвки в игре видна вертикальная «пила» посреди дороги. Гасим последние 15 %
    # ширины — в сцене эта зона уходит за Екатерину, шва не видно.
    ca = np.asarray(crop.split()[-1]).astype(np.float32)
    w = ca.shape[1]
    ramp_w = int(w * 0.15)
    ramp = np.ones(w, np.float32)
    ramp[w - ramp_w:] = np.linspace(1.0, 0.0, ramp_w)
    ca = ca * ramp[None, :]
    crop.putalpha(Image.fromarray(ca.astype(np.uint8)))
    print('правый край растушёван: последние %d px из %d' % (ramp_w, w))
    print('%s: bbox %s  (%dx%d из %dx%d), фон снят %.0f%%'
          % (name, box, crop.width, crop.height, rgba.width, rgba.height, 100 * st['removed']))
    return crop, np.asarray(crop.split()[-1]) > 90


bench, bm = prep('bench_long')
dst = os.path.join(SPR, 'prop_bench.png')
bench.save(dst)

# профиль по строкам: сколько дерева в средней половине ширины
h, w = bm.shape
mid = bm[:, int(w * 0.28):int(w * 0.72)]
print('профиль дерева по строкам (средняя половина ширины), h=%d:' % h)
for y in range(0, h, max(1, h // 24)):
    row = mid[y]
    c = np.nonzero(row)[0]
    span = (c.max() - c.min()) if len(c) else 0
    print('  y %3d%%  заполнено %4.0f%%  размах %4.0f%%'
          % (100 * y / h, 100 * row.mean(), 100 * span / mid.shape[1]))

# ASCII силуэт
cols = 56
rows = max(1, int(round(cols * h / w * 0.5)))
ch, cw = h / rows, w / cols
print('силуэт (%dx%d):' % (w, h))
for ry in range(rows):
    print('%3d %s' % (ry, ''.join(
        '#' if bm[int(ry * ch):int((ry + 1) * ch), int(rx * cw):int((rx + 1) * cw)].mean() > .5
        else ('+' if bm[int(ry * ch):int((ry + 1) * ch), int(rx * cw):int((rx + 1) * cw)].mean() > .15
              else '.') for rx in range(cols))))
print('-> %s (%dx%d)' % (os.path.relpath(dst, HERE), bench.width, bench.height))
