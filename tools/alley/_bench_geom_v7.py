# -*- coding: utf-8 -*-
"""Проверка геометрии v7 без рендера: где стоят доски спинки относительно стоек.

Считает в плоскости (u, v): u — нормаль к спинке (на наблюдателя), v — вдоль наклона.
Для каждой доски и каждой стойки печатает диапазоны u и y и вердикт «пересекается / нет».
"""
import math

L = 1.80
SEAT_DEPTH = 0.56
SLAT_T = 0.034
T = math.radians(10.0)
LEG = 0.072
BACK_X = -SEAT_DEPTH / 2 + 0.035
POST_Y = L / 2 - 0.075
BSW = 0.100
ZS = (0.560, 0.695, 0.830)
BACK_TOP = 0.90


def leg_x(z):
    return BACK_X - z * math.tan(T)


def report(mode):
    if mode == 'A':
        slat_len = 2.0 * (POST_Y - LEG / 2) - 0.004
        off = (LEG - SLAT_T) / 2.0
    else:
        slat_len = L
        off = (LEG + SLAT_T) / 2.0
    print('\n=== режим %s: длина доски %.3f, сдвиг по нормали %.3f' % (mode, slat_len, off))
    print('стойка: u = %.3f..%.3f, y = %.3f..%.3f (ось y=±%.3f)'
          % (-LEG / 2, LEG / 2, -LEG / 2, LEG / 2, POST_Y))
    for i, z in enumerate(ZS):
        u0, u1 = off - SLAT_T / 2, off + SLAT_T / 2
        y0, y1 = -slat_len / 2, slat_len / 2
        post_in = POST_Y - LEG / 2
        overlap_y = not (y1 <= post_in or y0 >= -post_in)
        overlap_u = not (u1 <= -LEG / 2 or u0 >= LEG / 2)
        print('  доска %d: u %.3f..%.3f  y %.3f..%.3f  | зазор до передней грани стойки '
              '%+.3f м | y-пересечение: %s | u-пересечение: %s -> %s'
              % (i, u0, u1, y0, y1, u0 - LEG / 2,
                 'да' if overlap_y else 'нет', 'да' if overlap_u else 'нет',
                 'ВРЕЗАЕТСЯ' if (overlap_u and overlap_y) else 'чисто'))
    # проверка наклона: верх стойки должен быть ПОЗАДИ низа
    zb, zt = 0.0, BACK_TOP
    print('  ось стойки: низ x=%.3f, верх x=%.3f -> верх %s (наклон %.1f°)'
          % (leg_x(zb), leg_x(zt), 'позади' if leg_x(zt) < leg_x(zb) else 'ВПЕРЕДИ',
             math.degrees(T)))


for m in ('A', 'B'):
    report(m)
