# -*- coding: utf-8 -*-
"""Дорастить правую переднюю ножку новой скамейки до линии земли.

Замер: в `prop_bench_new_matte.png` дальняя передняя ножка кончается на y=531, а линия
земли (по правилу: линия низа передних ножек идёт в точку схода, наклон 23.6°) на её
x=1348 должна быть на y=649. Не хватает 118 px файла.

Что делаю: беру НИЖНЮЮ часть этой же ножки (последние 90 строк её маски), растягиваю по
вертикали до нужной длины, приклеиваю под исходный низ с плавным стыком по альфе.
Дорисовки «из головы» нет — продолжение того же дерева.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, '_sat', 'prop_bench_new_matte.png')
OUT = os.path.join(ROOT, '_sat', 'prop_bench_new_fixed2.png')
SLOPE = np.tan(np.radians(23.6))
NEAR_FRONT = (555.0, 995.0)


def ground(x):
    return NEAR_FRONT[1] - SLOPE * (x - NEAR_FRONT[0])


def main():
    im = Image.open(SRC).convert('RGBA')
    a = np.asarray(im)
    m = a[:, :, 3] > 140
    Hf, Wf = m.shape

    # область правой передней ножки: последние 12% ширины
    x0, x1 = int(Wf * 0.88), Wf
    sub = m[:, x0:x1]
    ys, xs = np.nonzero(sub)
    print('ножка в области x %d..%d: маска y %d..%d, x %d..%d'
          % (x0, x1, ys.min(), ys.max(), x0 + xs.min(), x0 + xs.max()))
    y_bot = int(ys.max())
    x_leg_mid = x0 + int(xs.mean())
    target = ground(x_leg_mid)
    print('низ ножки y=%d, нужная земля на x=%.0f -> y=%.0f, дорастить %.0f px'
          % (y_bot, x_leg_mid, target, target - y_bot))

    need = int(round(target - y_bot))
    if need <= 0:
        print('ничего доращивать не надо')
        im.save(OUT)
        return

    # нижняя часть ножки — образец текстуры
    src_y0 = y_bot - 90
    patch = im.crop((x0, src_y0, x1, y_bot + 1))
    grown = patch.resize((patch.width, need + 4), Image.LANCZOS)

    out = im.copy()
    # плавный стык: альфа растушёвки сверху доращивания
    ga = np.asarray(grown).astype(np.float32)
    fade = np.linspace(0.0, 1.0, ga.shape[0])[:, None]
    ga[:, :, 3] = ga[:, :, 3] * np.clip(fade * 1.6, 0, 1)
    grown = Image.fromarray(ga.astype(np.uint8), 'RGBA')
    # вставляем так, чтобы доращивание закончилось ровно на линии земли
    out.alpha_composite(grown, (x0, int(round(target - grown.height))))
    out.save(OUT)

    b = np.asarray(out)
    mm = b[:, :, 3] > 140
    sub2 = mm[:, x0:x1]
    ys2 = np.nonzero(sub2)[0]
    print('после правки: низ ножки y=%d (земля %.0f, разница %+.0f px)'
          % (ys2.max(), target, ys2.max() - target))
    print('saved', os.path.relpath(OUT, HERE), os.path.getsize(OUT), 'B')


if __name__ == '__main__':
    main()
