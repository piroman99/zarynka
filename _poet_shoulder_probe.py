# -*- coding: utf-8 -*-
"""Стабильная мерка масштаба фигуры: ширина ПЛЕЧ (пояс 0.35–0.55 высоты bbox).

Ширина головы не годится для сравнения: у длинноволосого в «голову» попадает масса
волос, у стриженого — только череп. Плечи от причёски не зависят.

Печатает для каста (эталон) и для сырых эмоций поэта:
  плечи/рост = shoulderW / bboxH  — именно это определяет видимый размер в движке,
  потому что .sprite{height:99%} масштабирует картинку по высоте холста.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
SPR = os.path.join(HERE, 'assets', 'sprites')


def mask_of(path):
    im = Image.open(path)
    if im.mode == 'RGBA':
        return np.asarray(im.split()[-1]) > 128
    a = np.asarray(im.convert('RGB'), np.int16)
    h = a.shape[0]
    ring = np.concatenate([a[:8].reshape(-1, 3), a[:h * 3 // 5, :8].reshape(-1, 3),
                           a[:h * 3 // 5, -8:].reshape(-1, 3)])
    seed = np.median(ring, 0)
    return np.sqrt(((a - seed) ** 2).sum(2)) > 40


def measure(path):
    m = mask_of(path)
    ys, xs = np.nonzero(m)
    y0, y1 = ys.min(), ys.max()
    bh = y1 - y0
    band = m[y0 + int(bh * 0.35):y0 + int(bh * 0.55)]
    cols = np.nonzero(band.any(0))[0]
    sh = int(cols.max() - cols.min()) if len(cols) else 0
    head = m[y0:y0 + max(4, int(bh * 0.30))]
    hx = np.nonzero(head.any(0))[0]
    hw = int(hx.max() - hx.min()) if len(hx) else 0
    return dict(canvas=m.shape, bboxH=bh, shoulder=sh, head=hw,
                r_sh=sh / m.shape[0], r_head=hw / m.shape[0])


print('--- ЭТАЛОН КАСТА (vn2/img/char, webp после сборки) ---')
for n in ('sergey.webp', 'kate.webp', 'starik_stern.webp'):
    p = os.path.join(HERE, 'vn2', 'img', 'char', n)
    if not os.path.exists(p):
        continue
    r = measure(p)
    print('%-18s canvas %s bboxH %4d плечи %4d  плечи/H %.3f  голова/H %.3f'
          % (n, r['canvas'], r['bboxH'], r['shoulder'], r['r_sh'], r['r_head']))

print('\n--- СЫРЫЕ ЭМОЦИИ ПОЭТА ---')
names = ['poet2_b_0.png', 'poet_ha_neutral', 'poet_ha_interested', 'poet_ha_upset',
         'poet_sh_neutral', 'poet_sh_tired', 'poet_sh_inspired']
for n in names:
    p = os.path.join(GEN, n) if n.endswith('.png') else None
    if p is None:
        for ext in ('.png', '.jpg'):
            q = os.path.join(GEN, n + '_0' + ext)
            if os.path.exists(q):
                p = q
                break
    if not p or not os.path.exists(p):
        print('нет', n)
        continue
    r = measure(p)
    print('%-22s canvas %s bboxH %4d плечи %4d  плечи/H %.3f  голова/H %.3f'
          % (n, r['canvas'], r['bboxH'], r['shoulder'], r['r_sh'], r['r_head']))
