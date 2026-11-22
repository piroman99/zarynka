# -*- coding: utf-8 -*-
"""Точная проверка ножек: где каждая ножка новой скамейки приземляется на асфальт.

Иван: «правая сторона взлетела, должна быть на 30–40 см ниже; правая задняя ножка летает».
Считаю по ножкам, а не на глаз: нахожу низ каждой ножки в файле пропа, прохожу через
масштаб+поворот+вставку и сравниваю с ЗЕМЛЁЙ, проведённой в точку схода ворот.

Правило перспективы: линия, соединяющая низ ПЕРЕДНИХ ножек, и линия низа ЗАДНИХ
одинаково параллельны оси аллеи и идут в её точку схода (наклон 23.6° в этом кадре).
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
Y_H, K = 572.0, 1.146
VANISH = (1037.0, 572.0)

PROPS = {
    'A старая': dict(path=os.path.join(ROOT, 'assets', 'sprites', 'prop_bench.png'),
                     leg_x=0.100, leg_y=0.881, top=0.160, axis=26.2,
                     near_back=(60, 200), near_front=(470, 620), far_back=None, far_front=None),
    'B новая': dict(path=os.path.join(ROOT, '_sat', 'prop_bench_new_matte.png'),
                    leg_x=0.0696, leg_y=0.8715, top=0.1295, axis=19.6,
                    near_back=(50, 200), near_front=(480, 620),
                    far_back=(990, 1100), far_front=(1290, 1380)),
}


def leg_bottoms(path, windows):
    a = np.asarray(Image.open(path).convert('RGBA'))
    m = a[:, :, 3] > 140
    out = {}
    for name, win in windows.items():
        if not win:
            continue
        x0, x1 = win
        best = None
        for x in range(x0, min(x1, m.shape[1])):
            col = np.nonzero(m[:, x])[0]
            if not col.size:
                continue
            if best is None or col.max() > best[1]:
                best = (x, col.max())
        if best:
            out[name] = best
    return out


def main():
    for label, cfg in PROPS.items():
        print('\n=== %s' % label)
        legs = leg_bottoms(cfg['path'], {'near_back': cfg['near_back'],
                                         'near_front': cfg['near_front'],
                                         'far_back': cfg['far_back'],
                                         'far_front': cfg['far_front']})
        y_leg, x_leg = 960.0, 148.0
        m_scene = K * (y_leg - Y_H)
        alley = np.degrees(np.arctan2(y_leg - VANISH[1], VANISH[0] - x_leg))
        rot = alley - cfg['axis']
        th = np.deg2rad(rot)
        print('поворот %.1f°, %.0f px/м' % (rot, m_scene))

        for name, (xf, yf) in sorted(legs.items()):
            print('  %-10s файл (%4d, %4d)' % (name, xf, yf))
        # низ ближней задней — якорь
        bx, by = legs['near_back']
        for name, (xf, yf) in sorted(legs.items()):
            dxs = xf - bx
            dys = yf - by
            # поворот вокруг якоря (в экранных координатах y вниз)
            rx = dxs * np.cos(th) + dys * np.sin(th)
            ry = -dxs * np.sin(th) + dys * np.cos(th)
            # масштаб: k подобран так, что высота ближнего торца = 0.90 м; оценим по
            # соотношению уже применённому: k = 0.90*m / (span*Hf) — передаётся извне
            print('   %-10s смещение от якоря в файле (%+.0f, %+.0f) => после поворота (%+.0f, %+.0f)'
                  % (name, dxs, dys, rx, ry))


if __name__ == '__main__':
    main()
