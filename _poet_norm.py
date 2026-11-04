# -*- coding: utf-8 -*-
"""Нормировка эмоций поэта под ОДНУ крупность (0 ₽, без генерации).

Зачем: движок ставит спрайт как `.sprite{bottom:-3%;height:99%}` — картинка
масштабируется ПО ВЫСОТЕ холста, поэтому видимый размер фигуры = плечи/высота_холста.
gpt-image-2 отдал разные кадры (864x1152, 1086x1448, 1254x1254 квадрат), и без нормировки
при смене эмоции «прыгает» голова.

Мерка — ШИРИНА ПЛЕЧ (пояс 35–55 % высоты фигуры): от причёски не зависит, в отличие от
ширины головы (у длинноволосого в «голову» попадает масса волос).

Эталон: Сергей `vn2/img/char/sergey.webp` — плечи/холст = 0.559. К нему и приводим.

Как: холст = фигура, обрезанная по bbox; высоту холста подгоняем так, чтобы
плечи/высота = TARGET_SH: не хватает высоты — прозрачный паддинг СВЕРХУ (низ фигуры
остаётся на нижней кромке), избыток — подрезка СНИЗУ (видно меньше торса).

Результат: `assets/sprites/poet_<emo>.png`. Проверка — `_poet_scale_check.py`.
"""
import os
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
SPR = os.path.join(HERE, 'assets', 'sprites')
os.makedirs(SPR, exist_ok=True)

TARGET_SH = 0.56          # плечи / высота холста (Сергей 0.559)
SIDE_MARGIN = 0.03        # поля по бокам, доля ширины фигуры


def cutout(im, tol=34):
    a = np.asarray(im.convert('RGB'), np.float32)
    h, w, _ = a.shape
    ring = np.concatenate([a[:8].reshape(-1, 3),
                           a[:h * 3 // 5, :8].reshape(-1, 3),
                           a[:h * 3 // 5, -8:].reshape(-1, 3)])
    seed = np.median(ring, 0)
    cand = np.sqrt(((a - seed) ** 2).sum(2)) <= tol
    vis = np.zeros((h, w), bool)
    dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if cand[y, x] and not vis[y, x]:
                vis[y, x] = True
                dq.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if cand[y, x] and not vis[y, x]:
                vis[y, x] = True
                dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and cand[ny, nx] and not vis[ny, nx]:
                vis[ny, nx] = True
                dq.append((ny, nx))
    A = Image.fromarray(np.where(vis, 0, 255).astype(np.uint8), 'L').filter(
        ImageFilter.GaussianBlur(1.1))
    out = im.convert('RGBA')
    out.putalpha(A)
    return out


def shoulders(mask):
    ys, xs = np.nonzero(mask)
    y0, y1 = ys.min(), ys.max()
    bh = y1 - y0
    band = mask[y0 + int(bh * 0.35):y0 + int(bh * 0.55)]
    cols = np.nonzero(band.any(0))[0]
    return (int(cols.max() - cols.min()) if len(cols) else 0), bh


def norm(path, name):
    rgba = cutout(Image.open(path))
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
        keep = fig.crop((0, 0, fig.width, canvas_h))
        canvas.alpha_composite(keep, (mw, 0))
        mode = 'подрезка снизу %d px' % (fh - canvas_h)
    out = os.path.join(SPR, 'poet_%s.png' % name)
    # СОХРАНЯЕМ НА СВЕТЛО-СЕРОМ ФОНЕ (RGB), а не прозрачным: сборка сама прогоняет
    # cutout() по всем CHAR_SRC, и повторная вырезка по уже прозрачному PNG съела бы
    # тёмные волосы (конверт в RGB даёт чёрный фон, он в допуске «фона»).
    flat = Image.new('RGB', canvas.size, (205, 205, 205))
    flat.paste(canvas, (0, 0), canvas)
    flat.save(out)
    m2 = np.asarray(canvas.split()[-1]) > 128
    sh2, _ = shoulders(m2)
    print('  %-16s %4dx%-4d -> %dx%d  плечи %d -> %.3f  (%s)'
          % (name, Image.open(path).width, Image.open(path).height, canvas_w, canvas_h,
             sh, sh2 / canvas_h, mode))
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
    print('нормировка эмоций поэта (плечи/холст = %.2f) -> assets/sprites/' % TARGET_SH)
    for key in FILES:
        if only and key not in only:
            continue
        p = find(key)
        if not p:
            print('  нет файла для', key)
            continue
        norm(p, key)
