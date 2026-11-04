# -*- coding: utf-8 -*-
"""Нормировка эмоций поэта под ОДНУ крупность (0 ₽, без генерации).

Зачем: движок ставит спрайт как `.sprite{bottom:-3%;height:99%}` — картинка
масштабируется ПО ВЫСОТЕ холста, поэтому видимый размер фигуры = плечи/высота_холста.
gpt-image-2 отдал разные кадры (864x1152, 1086x1448, 1254x1254 квадрат), и без нормировки
при смене эмоции «прыгает» голова.

Мерка — ШИРИНА ПЛЕЧ (пояс 35–55 % высоты фигуры): от причёски не зависит, в отличие от
ширины головы (у длинноволосого в «голову» попадает масса волос).
Эталон: Сергей `vn2/img/char/sergey.webp` — плечи/холст = 0.559.

Вырезание — НЕ `cutout()` сборки, а `_poet_matte.matte()`: мягкая альфа по цвету фона,
удаление ЗАМКНУТЫХ областей фона (петли волос) и despill серой каймы. Поэтому на выходе
RGBA, и сборка такие файлы больше не режет (см. CHAR_SRC в `_vn2_build.py`).

Результат: `assets/sprites/poet_<emo>.png`. Проверка — `_poet_scale_check.py`,
ровность края — `_poet_hair_check.py`.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _poet_matte import matte  # noqa: E402

GEN = os.path.join(HERE, 'assets', 'gen')
SPR = os.path.join(HERE, 'assets', 'sprites')
os.makedirs(SPR, exist_ok=True)

TARGET_SH = 0.56          # плечи / высота холста (Сергей 0.559)
SIDE_MARGIN = 0.03        # поля по бокам, доля ширины фигуры


def shoulders(mask):
    ys, xs = np.nonzero(mask)
    y0, y1 = ys.min(), ys.max()
    bh = y1 - y0
    band = mask[y0 + int(bh * 0.35):y0 + int(bh * 0.55)]
    cols = np.nonzero(band.any(0))[0]
    return (int(cols.max() - cols.min()) if len(cols) else 0), bh


def norm(path, name):
    rgba, st = matte(Image.open(path))
    mask = np.asarray(rgba.split()[-1]) > 128
    sh, bh = shoulders(mask)
    if not sh:
        print('  %-16s плечи не найдены — пропуск' % name)
        return None
    canvas_h = int(round(sh / TARGET_SH))
    ys, xs = np.nonzero(mask)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    fig = rgba.crop((x0, y0, x1 + 1, y1 + 1))
    fh = fig.height
    mw = int(round(fig.width * SIDE_MARGIN))
    canvas_w = fig.width + 2 * mw
    canvas = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    if canvas_h >= fh:                      # не хватает высоты -> паддинг сверху
        canvas.alpha_composite(fig, (mw, canvas_h - fh))
        mode = 'паддинг сверху %d px' % (canvas_h - fh)
    else:                                   # избыток -> подрезка снизу
        canvas.alpha_composite(fig.crop((0, 0, fig.width, canvas_h)), (mw, 0))
        mode = 'подрезка снизу %d px' % (fh - canvas_h)
    out = os.path.join(SPR, 'poet_%s.png' % name)
    canvas.save(out)
    m2 = np.asarray(canvas.split()[-1]) > 128
    sh2, _ = shoulders(m2)
    print('  %-16s %4dx%-4d -> %dx%d  плечи %d -> %.3f  (%s, фон снят %.0f%%)'
          % (name, Image.open(path).width, Image.open(path).height, canvas_w, canvas_h,
             sh, sh2 / canvas_h, mode, 100 * st['removed']))
    return out


FILES = ['ha_neutral', 'ha_interested', 'ha_upset',
         'sh_neutral', 'sh_tired', 'sh_inspired']


def find(name):
    for ext in ('.png', '.jpg'):
        p = os.path.join(GEN, 'poet_%s_0%s' % (name, ext))
        if os.path.exists(p):
            return p
    return None


if __name__ == '__main__':
    only = sys.argv[1:]
    print('нормировка эмоций поэта (плечи/холст = %.2f, матирование _poet_matte) -> assets/sprites/'
          % TARGET_SH)
    for key in FILES:
        if only and key not in only:
            continue
        p = find(key)
        if not p:
            print('  нет файла для', key)
            continue
        norm(p, key)
