# -*- coding: utf-8 -*-
"""Убирает белую кайму (matte fringe) по краю спрайта — локально, без новых генераций.

Причина каймы: спрайт вырезали с белого фона, крайние пиксели смешаны с белым
(замер: яркость кромки 152.5 против 70.3 в ядре, 6068 светлых пикселей на кромке).

Лечение в два шага:
  1) ЦВЕТ: подтягиваем цвет кромки изнутри — итеративно заполняем внешнюю зону
     цветом соседних внутренних пикселей (никакого придумывания, только перенос
     уже существующих цветов тела).
  2) АЛЬФА: срезаем 1 px полупрозрачной бахромы и заново сглаживаем, чтобы край
     остался мягким, но без светлого ободка.

Вход/выход через env: SRC, DST, ERODE (px), FEATHER (px).
"""
import os

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CHAR = os.path.join(ROOT, 'vn2', 'img', 'char')
SRC = os.path.join(CHAR, os.environ.get('SRC', 'poet_seat_upset.webp'))
DST = os.path.join(CHAR, os.environ.get('DST', 'poet_seat_upset_fixed.webp'))
ERODE = int(os.environ.get('ERODE', '1'))
FEATHER = float(os.environ.get('FEATHER', '0.6'))
FILL_PASSES = int(os.environ.get('FILL_PASSES', '10'))


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


def dilate(mask, n=1):
    m = mask.copy()
    for _ in range(n):
        d = m.copy()
        d[1:, :] |= m[:-1, :]
        d[:-1, :] |= m[1:, :]
        d[:, 1:] |= m[:, :-1]
        d[:, :-1] |= m[:, 1:]
        m = d
    return m


def main():
    im = Image.open(SRC).convert('RGBA')
    arr = np.asarray(im).astype(np.float32)
    rgb, al = arr[:, :, :3].copy(), arr[:, :, 3].copy()
    h, w = al.shape

    alpha01 = al / 255.0
    solid = alpha01 > 0.95
    known = erode(solid, 2)                 # заведомо «внутренние» пиксели
    unknown = ~known

    # --- шаг 1: заполнение цвета изнутри (перенос известных цветов наружу) ---
    col = rgb.copy()
    known_m = known.copy()
    for _ in range(FILL_PASSES):
        if not unknown.any():
            break
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
        col[newly] = acc[newly] / cnt[newly][:, None]
        known_m = known_m | newly

    # --- шаг 2: альфа без бахромы ---
    a = Image.fromarray(al.astype(np.uint8), 'L')
    m = np.asarray(a) > 40
    m2 = erode(m, ERODE)
    # обратно в плавную альфу: слегка размыть
    a2 = Image.fromarray((m2 * 255).astype(np.uint8), 'L')
    if FEATHER > 0:
        a2 = a2.filter(ImageFilter.GaussianBlur(FEATHER))
    a2 = a2.point(lambda v: 0 if v < 12 else min(255, int(v * 1.04)))

    out = np.dstack([col.clip(0, 255), np.asarray(a2, dtype=np.float32)])
    img = Image.fromarray(out.astype(np.uint8), 'RGBA')
    img.save(DST, lossless=True, quality=100, method=6)
    print('saved %s %dx%d %d B' % (os.path.relpath(DST, HERE), img.width, img.height,
                                   os.path.getsize(DST)))

    # --- контроль: повторный замер кромки на новом файле ---
    b = np.asarray(img).astype(float)
    bl = b[:, :, 3]
    blum = 0.299 * b[:, :, 0] + 0.587 * b[:, :, 1] + 0.114 * b[:, :, 2]
    bs = bl > 128
    be = bs & ~erode(bs, 2)
    core = blum[bl > 230].mean()
    print('после: яркость кромки %.1f, ядро %.1f (разница %+.1f); светлых на кромке %d'
          % (blum[be].mean(), core, blum[be].mean() - core,
             (be & (blum > core + 25)).sum()))
    dfr = (bl > 20) & (bl <= 180)
    print('       полупрозрачная бахрома %d px (было 3167)' % dfr.sum())


if __name__ == '__main__':
    main()
