# -*- coding: utf-8 -*-
"""Замеры, на которых держится посадка поэта (все — из пикселей, без анатомии).

1) F_SEAT — доля файла, где силуэт ПОПЕРЁК ещё цельный, а ниже распадается на две
   ноги: именно эта линия ложится на доску сиденья.
2) F_FEET — низ силуэта.
3) GROUND — контакт передних ножек скамейки с землёй в кадре (низ альфы пропа).
   Ноги сидящего свисают вперёд, к зрителю, то есть на той же глубине.
4) H — из двух жёстких связей: таз на доске, ступни на земле.
   H = (GROUND - SEAT) / (F_FEET - F_SEAT)  — не выбирается, а следует.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PROP = os.path.join(ROOT, '_sat', 'wc', os.environ.get('PROP', 'prop_B.png'))
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
Y_GROUND_LEG = 960.0
PROP_W = 876


def runs_of(row, min_len=10):
    """списки непрерывных непрозрачных отрезков в строке (длиннее min_len)."""
    out, s = [], None
    w = len(row)
    for x in range(w + 1):
        v = row[x] if x < w else False
        if v and s is None:
            s = x
        elif not v and s is not None:
            if x - s >= min_len:
                out.append((s, x - 1))
            s = None
    return out


def split_row(m):
    """строка, где силуэт перестаёт распадаться на две ноги (контакт с сиденьем).

    Идём СНИЗУ вверх: внизу две ноги — два отрезка; на уровне доски они
    сливаются в один. Возвращаем последнюю строку с двумя отрезками и первую слитную.
    """
    h, w = m.shape
    two_rows = []
    for y in range(int(h * 0.98), int(h * 0.45), -1):
        if len(runs_of(m[y])) >= 2:
            two_rows.append(y)
        elif two_rows:
            return two_rows[-1], y
    return (two_rows[-1] if two_rows else None), None


def main():
    poet = Image.open(POET).convert('RGBA')
    pa = np.asarray(poet)[:, :, 3] > 100
    ph, pw = pa.shape
    rows = np.nonzero(pa.any(axis=1))[0]
    f_top, f_feet = rows.min() / ph, rows.max() / ph
    solid, split = split_row(pa)
    print('спрайт %dx%d: верх %.3f, низ %.3f' % (pw, ph, f_top, f_feet))
    print('силуэт цельный до строки %d (%.3f), распадается на ноги с %d (%.3f)'
          % (solid, solid / ph, split, split / ph))
    f_seat = (solid + 1) / ph
    print('F_SEAT = %.4f, F_FEET = %.4f' % (f_seat, f_feet))

    prop = Image.open(PROP).convert('RGBA')
    a = np.asarray(prop)[:, :, 3]
    m = a > 60
    prows = np.nonzero(m.any(axis=1))[0]
    pcols = np.nonzero(m.any(axis=0))[0]
    px = int(round(0.2856 * Y_GROUND_LEG - 108.5 + 15 - pcols.min()))
    py = int(round(Y_GROUND_LEG - prows.max()))
    print('\nпроп: левый %d, верх %d -> вставка (%d, %d)' % (pcols.min(), prows.min(), px, py))

    # доска: последняя длинная полоса в колонке поэта
    poet_col = int(os.environ.get('POET_COL', '343'))
    col = m[:, poet_col]
    runs, s = [], None
    for y in range(len(col) + 1):
        v = col[y] if y < len(col) else False
        if v and s is None:
            s = y
        elif not v and s is not None:
            runs.append((s, y - 1))
            s = None
    seat_local = runs[-1][0]
    seat_frame = py + seat_local

    # земля ПОД СИДЕНЬЕМ: из связи высоты (сиденье 0.45 м над землёй)
    CAMH = 0.872600
    K, Y_H = 1.146, 572.0
    g_local = seat_frame + 0.45 * (seat_frame - Y_H) / CAMH
    for _ in range(40):
        g_local = seat_frame + 0.45 * (g_local - Y_H) / CAMH
    # ступни свисают вперёд, к зрителю, на ~0.30 м => ниже по экрану на forward_px
    forward_px = float(os.environ.get('FORWARD_PX', '46'))
    ground_feet = g_local + forward_px
    print('доска в пропе y=%d -> кадр %d' % (seat_local, seat_frame))
    print('земля под сиденьем %.1f, ступни впереди -> %.1f (низ пропа, передние ножки, %d)'
          % (g_local, ground_feet, py + prows.max()))
    ground = ground_feet

    h_px = (ground - seat_frame) / (f_feet - f_seat)
    top = int(round(ground - f_feet * h_px))
    print('H = %.1f px  (фигура %.1f px), верх спрайта в кадре %d' % (h_px, (f_feet - f_top) * h_px, top))

    K, Y_H = 1.146, 572.0
    m_feet = K * (ground - Y_H)
    print('масштаб у ног %.0f px/м -> фигура %.2f м' % (m_feet, (f_feet - f_top) * h_px / m_feet))

    # контроль обоих контактов
    butt_frame = top + f_seat * h_px
    feet_frame = top + f_feet * h_px
    print('\nконтроль: таз %.1f против доски %d (дельта %+.1f px)'
          % (butt_frame, seat_frame, butt_frame - seat_frame))
    print('          ступни %.1f против земли %d (дельта %+.1f px)'
          % (feet_frame, ground, feet_frame - ground))

    out = dict(f_seat=f_seat, f_feet=f_feet, h_px=float(h_px), top=int(top), px=int(px),
               py=int(py), seat_frame=int(seat_frame), ground=int(ground),
               x_poet=int(os.environ.get('POET_X', '421')))
    import json
    with open(os.path.join(ROOT, '_sat', 'poet_params.json'), 'w') as f:
        json.dump(out, f, indent=2)
    print('\nзаписано _sat/poet_params.json')


if __name__ == '__main__':
    main()
