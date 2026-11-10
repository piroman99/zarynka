# -*- coding: utf-8 -*-
"""Убираем НАРИСОВАННУЮ в фоне скамейку (левый низ кадра), чтобы не было двух скамеек.

Замер `_bgbench_left.py`: пятно «дерева» в фоне занимает x 12..246, y 858..972 (1920x1080),
это нарисованная мебель у самого края кадра — из-под пропа она торчит и читается как
вторая скамейка.

Метод: диффузионная заливка (итеративное усреднение от границы) внутри маски + мягкая
растушёвка края. Никакой генерации, 0 ₽, исходный файл не трогаем: пишем отдельный
assets/gen/alley_b_clean_0.png, его и берёт сборка.
"""
import os
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'assets', 'gen', 'alley_b_0.jpg')
DST = os.path.join(HERE, 'assets', 'gen', 'alley_b_clean_0.png')

X0, X1, Y0, Y1 = 0, 250, 715, 941      # прямоугольник заливки (с запасом вокруг пятна)
# Координаты — в системе ИСХОДНИКА (1672x941). Пятно скамейки, найденное на клиенте
# (1920x1080: x 12..246, y 858..972), пересчитано: x 10..214, y 747..846.

im = Image.open(SRC).convert('RGB')
W, H = im.size
print('фон %dx%d' % (W, H))
a = np.asarray(im).astype(np.float32)

# маска: прямоугольник, но по краям — мягкая (растушёвка 18 px)
mask = np.zeros((H, W), np.float32)
mask[Y0:Y1, X0:X1] = 1.0
mk = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18))
mask = np.asarray(mk).astype(np.float32) / 255.0

hard = mask > 0.5
ys, xs = np.nonzero(hard)
print('заливаем: x %d..%d, y %d..%d (%d px)' % (xs.min(), xs.max(), ys.min(), ys.max(),
                                                hard.sum()))

# диффузия: стартуем со среднего по границе, потом усредняем соседей внутри маски
work = a.copy()
ring = (mask > 0.02) & (mask < 0.98)
work[hard] = a[ring].mean(0)
for it in range(600):
    up = np.roll(work, 1, 0)
    dn = np.roll(work, -1, 0)
    lf = np.roll(work, 1, 1)
    rt = np.roll(work, -1, 1)
    avg = (up + dn + lf + rt) * 0.25
    work[hard] = avg[hard]
# лёгкое размытие внутри — чтобы не было ступенек от итераций
blur = np.asarray(Image.fromarray(work.astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))
                  ).astype(np.float32)
work[hard] = blur[hard]

out = a * (1 - mask[..., None]) + work * mask[..., None]
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(DST)
print('->', os.path.relpath(DST, HERE))

# проверка: сколько «дерева» осталось в бывшем пятне
chk = Image.open(DST).convert('RGB')
hsv = np.asarray(chk.convert('HSV')).astype(np.int16)
Hc, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
wood = (Hc >= 6) & (Hc <= 32) & (S >= 55) & (V >= 45) & (V <= 210)
print('«дерево» в пятне: стало %.1f%%' % (100 * wood[747:847, 10:215].mean()))
print('«дерево» в полосе заливки после: %.2f%%' % (100 * wood[715:941, 0:250].mean()))
src_hsv = np.asarray(Image.open(SRC).convert('HSV')).astype(np.int16)
sw = ((src_hsv[..., 0] >= 6) & (src_hsv[..., 0] <= 32) & (src_hsv[..., 1] >= 55) &
      (src_hsv[..., 2] >= 45) & (src_hsv[..., 2] <= 210))
print('«дерево» там же в исходнике: %.2f%%' % (100 * sw[715:941, 0:250].mean()))
