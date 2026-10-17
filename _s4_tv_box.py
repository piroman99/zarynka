# -*- coding: utf-8 -*-
"""Точные границы ТВ-экрана: ищем тёмную панель (звёздное поле) внутри светлого корпуса."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, 'assets/final/prolog/s4.png')).convert('RGB')
W, H = im.size
a = np.asarray(im).astype(np.float32)
lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)

# окно, где заведомо есть ТВ
AX0, AX1, AY0, AY1 = 500, 1400, 100, 600
sub = lum[AY0:AY1, AX0:AX1]
# тёмное звёздное поле: lum < 60
dark = sub < 60
# для каждой строки считаем протяжённость тёмного
rows = dark.mean(1)
cols = dark.mean(0)
ry = [AY0 + i for i in range(len(rows)) if rows[i] > 0.5]
rx = [AX0 + i for i in range(len(cols)) if cols[i] > 0.4]
print('строки панели:', min(ry), '..', max(ry))
print('столбцы панели:', min(rx), '..', max(rx))
y0, y1, x0, x1 = min(ry), max(ry), min(rx), max(rx)
print('экран 1920:', x0, y0, x1, y1, 'w=%d h=%d' % (x1 - x0, y1 - y0))
print('экран 2400 (x1.25):', x0 * 1.25, y0 * 1.25, x1 * 1.25, y1 * 1.25,
      'w=%.0f' % ((x1 - x0) * 1.25))

# корпус: яркая рамка вокруг -> ищем по градиенту
prof = lum[AY0:AY1, :].mean(0)
print('\nпрофиль lum по x (1500..1700 в 2400-пространстве = 1200..1360 в 1920):')
for x in range(1290, 1360, 2):
    print(x, round(float(prof[x]), 1))
