# -*- coding: utf-8 -*-
"""Числовая проверка кадра-карточки: остался ли белый ореол вокруг лого-круга."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, ".tmp_avmcheck", "big_card.png")
im = Image.open(p).convert("RGB")
a = np.asarray(im).astype(np.int16)
h, w, _ = a.shape
print("frame", w, h)

# ищем яркие пиксели (логотип кремовый ~ 244 / белый 255)
bright = a.min(axis=2) > 200
bright[600:, :] = False           # отрезаем заголовок, смотрим только лого
ys, xs = np.nonzero(bright)
if len(ys) == 0:
    print("лого не найдено")
    raise SystemExit
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
print("bbox яркого", x0, y0, x1, y1, "->", x1 - x0 + 1, "x", y1 - y0 + 1)
cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
rad = (x1 - x0 + 1) / 2
print("center", cx, cy, "rad", rad)

# доля почти-белых (>=250 по всем каналам) внутри bbox — «квадрат» бы дал углы
white = (a[y0:y1 + 1, x0:x1 + 1].min(axis=2) >= 250).mean()
print("доля белого (>=250) в bbox: %.4f" % white)
# углы bbox (внутри на 3 px) — там у круга должен быть фон
for name, (yy, xx) in {"tl": (y0 + 4, x0 + 4), "tr": (y0 + 4, x1 - 4),
                       "bl": (y1 - 4, x0 + 4), "br": (y1 - 4, x1 - 4)}.items():
    print(" угол", name, tuple(int(v) for v in a[yy, xx]))
# кольцо снаружи диска: радиус rad+3 .. rad+8 по 8 направлениям
import math
mx = 0
for ang in range(0, 360, 15):
    for dr in (2.0, 4.0, 6.0):
        x = int(round(cx + (rad + dr) * math.cos(math.radians(ang))))
        y = int(round(cy + (rad + dr) * math.sin(math.radians(ang))))
        if 0 <= x < w and 0 <= y < h:
            mx = max(mx, int(a[y, x].max()))
print("макс яркость сразу за диском:", mx, "(255 = белый ореол)")

# цвет фона карточки в углах кадра
for name, (yy, xx) in {"lt": (8, 8), "rt": (8, w - 9), "lb": (h - 9, 8), "rb": (h - 9, w - 9)}.items():
    print("фон", name, tuple(int(v) for v in a[yy, xx]))
