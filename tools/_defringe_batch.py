# -*- coding: utf-8 -*-
"""Пакетный дефринж спрайтов: убирает белую кайму по краю альфы.

Алгоритм тот же, что в alley/_poet_defringe.py (проверен на poet_seat_upset):
  1) ЦВЕТ: внешнюю зону заполняем цветом соседних внутренних пикселей
     (FILL_PASSES проходов) — ничего не придумываем, только перенос;
  2) АЛЬФА: срезаем ERODE px полупрозрачной бахромы, сглаживаем FEATHER,
     отбрасываем остатки ниже 12/255;
  3) пишем lossless webp (иначе квантование вернёт кайму).

Проверка на каждом файле:
  * внутренняя область (глубже 6 px) — |Δ| должно быть 0;
  * КАЙМА: яркость внешнего кольца силуэта против кольца 2..5 px внутри —
    разница должна быть < 12 (светлый КОНТЕНТ — руки, блики — присутствует
    и на внутреннем кольце, поэтому дельта около нуля; прежняя проверка
    «кромка против среднего по всему ядру» ложно ругалась на скин и блики);
  * число плотных пикселей не должно упасть больше чем на 1.5 % (не съели силуэт).

Режим: python3 _defringe_batch.py list | apply
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHAR = os.path.join(ROOT, 'vn2', 'img', 'char')

ERODE = 1
FEATHER = 0.6
FILL_PASSES = 10

TARGETS = [
    'poet.webp', 'poet_interested.webp', 'poet_upset.webp',
    'poet_seat.webp', 'poet_seat_interested.webp', 'poet_seat_shy.webp',
    'poet_seat_smile.webp', 'poet_seat_sullen.webp',
    'poet_sh.webp', 'poet_sh_inspired.webp', 'poet_sh_tired.webp',
    'poet_sit.webp', 'poet_sit_interested.webp', 'poet_sit_upset.webp',
    'sergey.webp', 'sergey_concerned.webp', 'sergey_smile.webp',
]


def erode(mask, n=1):
    m = mask.copy()
    for _ in range(n):
        e = m.copy()
        e[1:, :] &= m[:-1, :]
        e[:-1, :] &= m[1:, :]
        e[:, 1:] &= m[:, :-1]
        e[:, :-1] &= m[:, 1:]
        m = e
    return m


def lum_of(rgb):
    return 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]


def edge_stats(arr):
    """кайма: внешнее кольцо силуэта против кольца 2..5 px внутри."""
    al = arr[:, :, 3]
    lum = lum_of(arr[:, :, :3])
    solid = al > 200
    if solid.sum() < 100:
        return None
    r0 = solid & ~erode(solid, 1)
    r1 = erode(solid, 2) & ~erode(solid, 5)
    if not r1.any():
        return None
    return dict(edge=float(lum[r0].mean()), core=float(lum[r1].mean()),
                light=int((r0 & (lum > lum[r1].mean() + 40)).sum()),
                solid=int((al > 128).sum()))


def defringe(arr):
    rgb = arr[:, :, :3].astype(np.float32).copy()
    al = arr[:, :, 3].astype(np.float32).copy()
    h, w = al.shape

    solid = (al / 255.0) > 0.95
    known = erode(solid, 2)
    col = rgb.copy()
    known_m = known.copy()
    for _ in range(FILL_PASSES):
        acc = np.zeros_like(col)
        cnt = np.zeros((h, w), np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ys = slice(max(0, dy), h + min(0, dy))
            yd = slice(max(0, -dy), h + min(0, -dy))
            xs = slice(max(0, dx), w + min(0, dx))
            xd = slice(max(0, -dx), w + min(0, -dx))
            m_src = known_m[ys, xs]
            acc[yd, xd] += col[ys, xs] * m_src[..., None]
            cnt[yd, xd] += m_src
        newly = (~known_m) & (cnt > 0)
        if not newly.any():
            break
        col[newly] = acc[newly] / cnt[newly][:, None]
        known_m = known_m | newly

    m = al > 40
    m2 = erode(m, ERODE)
    a2 = Image.fromarray((m2 * 255).astype(np.uint8), 'L')
    if FEATHER > 0:
        a2 = a2.filter(ImageFilter.GaussianBlur(FEATHER))
    a2 = a2.point(lambda v: 0 if v < 12 else min(255, int(v * 1.04)))

    return np.dstack([col.clip(0, 255), np.asarray(a2, dtype=np.float32)]).astype(np.uint8)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'list'
    if mode == 'list':
        print('файлов к обработке: %d' % len(TARGETS))
        for t in TARGETS:
            p = os.path.join(CHAR, t)
            print('  %-28s %s' % (t, 'есть' if os.path.exists(p) else 'НЕТ'))
        return 0

    rows = []
    for name in TARGETS:
        p = os.path.join(CHAR, name)
        if not os.path.exists(p):
            print('НЕТ ФАЙЛА %s' % name)
            continue
        im = Image.open(p).convert('RGBA')
        before = np.asarray(im)
        b = edge_stats(before)

        out = defringe(before)
        a = edge_stats(out)

        deep = erode(before[:, :, 3] > 250, 6)
        dmax = float(np.abs(before[:, :, :3].astype(int) - out[:, :, :3].astype(int)).max(axis=2)[deep].max()) if deep.any() else -1
        dmean = float(np.abs(before[:, :, :3].astype(int) - out[:, :, :3].astype(int)).max(axis=2)[deep].mean()) if deep.any() else -1

        dst = Image.fromarray(out, 'RGBA')
        dst.save(p, lossless=True, quality=100, method=6)

        drop = 100.0 * (b['solid'] - a['solid']) / max(1, b['solid'])
        ok = (dmax == 0) and (a['edge'] - a['core'] < 12) and (drop < 1.5)
        rows.append((name, b, a, dmax, dmean, drop, ok))
        print('%-28s кайма %5.1f -> %5.1f (внутри %5.1f, Δ %+5.1f)  светлых %4d -> %3d  '
              'плотных %+4.2f%%  внутри |Δ| max %.0f ср %.2f  %s'
              % (name, b['edge'], a['edge'], a['core'], a['edge'] - a['core'],
                 b['light'], a['light'], -drop, dmax, dmean,
                 'OK' if ok else '!!! ПРОВЕРИТЬ'))

    bad = [r[0] for r in rows if not r[6]]
    print('\nобработано: %d, проблемных: %d' % (len(rows), len(bad)))
    if bad:
        print('проверить вручную: %s' % ', '.join(bad))
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
