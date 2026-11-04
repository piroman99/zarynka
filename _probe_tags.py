# -*- coding: utf-8 -*-
"""Есть ли на финальном кадре метка сцены (чёрная плашка + золотой текст в левом верху)?

    python3 _probe_tags.py

Метка рисуется в пространстве 2400x1350: прямоугольник (70,70)-(~x,128), текст в (90,82).
В 1920x1080 это (56,56)-(…,102) / текст в (72,66). Печатаем минимум/среднее яркости в
полосе и долю «золотых» пикселей (R>150, G>110, B<130) — у плашки с текстом она не нулевая.
"""
import os
import numpy as np
from PIL import Image

FIN = os.path.join('assets', 'final', 'prolog')


def probe(name):
    p = os.path.join(FIN, name + '.png')
    if not os.path.exists(p):
        return None
    a = np.asarray(Image.open(p).convert('RGB'), np.float32)
    h, w, _ = a.shape
    band = a[int(0.045 * h):int(0.095 * h), int(0.025 * w):int(0.42 * w)]
    dark = (band.mean(2) < 30).mean()
    gold = ((band[..., 0] > 150) & (band[..., 1] > 110) & (band[..., 2] < 140)).mean()
    return dict(size=(w, h), dark=round(float(dark), 3), gold=round(float(gold), 4),
                mean=round(float(band.mean()), 1))


for n in ('s1', 'p6', 'p7', 'p8', 's3', 's4', 's5a', 's6'):
    r = probe(n)
    print('%-4s %s' % (n, r))
