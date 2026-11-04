# -*- coding: utf-8 -*-
"""Быстрая численная проверка новых кадров (без глаз): размер, палитра, «чернила» граффити.

  python3 _probe_new_frames.py

Считает для каждого кадра:
  - размер/пропорции, средний RGB, насыщенность (для p6: палитра должна быть СЕРАЯ —
    марсианская охра/красная пыль = высокая доля красно-оранжевых пикселей);
  - «чернила» надписи: пиксели заметно темнее/цветнее стены в средней полосе кадра,
    их bbox в долях кадра и площадь (для s1wall — есть ли вообще надпись и где);
  - запас чёрного неба (p6: доля почти чёрных пикселей — лунное небо).
Плюс режет НАТИВНЫЕ кропы области надписи в `_sat/` для проверки букв глазами.
"""
import os
import numpy as np
from PIL import Image

GEN = 'assets/gen'
SAT = '_sat'
os.makedirs(SAT, exist_ok=True)

FRAMES = [
    ('s1wall_a', 's1wall_a__gpt-image-2_0.png'),
    ('s1wall_b', 's1wall_b__gpt-image-2_0.png'),
    ('p6luna_a', 'p6luna_a__gpt-image-2_0.jpg'),
    ('p6luna_b', 'p6luna_b__gpt-image-2_0.png'),
]


def stats(path):
    im = Image.open(path).convert('RGB')
    a = np.asarray(im, np.float32)
    h, w, _ = a.shape
    mx = a.max(2)
    mn = a.min(2)
    sat = (mx - mn) / np.maximum(mx, 1)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    ochre = (r > 95) & (r > g + 18) & (g > b + 10) & (r - b > 40)   # красная пыль/охра
    dark = mx < 40
    val = a.mean(2)
    return dict(im=im, a=a, h=h, w=w, sat=float(sat.mean()),
                ochre=float(ochre.mean()), dark=float(dark.mean()),
                mean=tuple(round(float(x), 1) for x in a.reshape(-1, 3).mean(0)),
                std=float(val.std()))


def ink_bbox(st, band=(0.25, 0.85)):
    """Пиксели надписи: заметно темнее локального фона или насыщенно цветные."""
    a, h, w = st['a'], st['h'], st['w']
    y0, y1 = int(band[0] * h), int(band[1] * h)
    reg = a[y0:y1]
    med = np.median(reg.reshape(-1, 3), 0)
    d = np.abs(reg - med).sum(2)
    mx = reg.max(2)
    sat = (mx - reg.min(2)) / np.maximum(mx, 1)
    m = (d > 130) | (sat > 0.45)
    m = m.reshape(reg.shape[0], reg.shape[1])
    # срезаем редкий шум: оставляем строки/столбцы с заметной плотностью
    rows = m.sum(1) > max(12, 0.02 * w)
    cols = m.sum(0) > max(12, 0.02 * h)
    if not rows.any() or not cols.any():
        return None
    ry = np.where(rows)[0]
    cx = np.where(cols)[0]
    return dict(frac=float(m.mean()), x0=float(cx[0] / w), x1=float(cx[-1] / w),
                y0=float((y0 + ry[0]) / h), y1=float((y0 + ry[-1]) / h))


def sheet(items, out):
    """Полосы A/B с подписями (это лист для просмотра, не кадр)."""
    from PIL import ImageDraw, ImageFont
    W = 1440
    bands = []
    for cap, im in items:
        h = round(im.height * W / im.width)
        bands.append((cap, im.resize((W, h), Image.LANCZOS), h))
    H = sum(b[2] + 34 for b in bands) + 10
    out_im = Image.new('RGB', (W, H), (14, 14, 16))
    d = ImageDraw.Draw(out_im)
    try:
        f = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Medium.ttf', 22)
    except Exception:
        f = ImageFont.load_default()
    y = 6
    for cap, im, h in bands:
        d.text((12, y), cap, font=f, fill=(240, 222, 180))
        y += 30
        out_im.paste(im, (0, y))
        y += h + 4
    out_im.save(out)
    return out


def main():
    items = []
    for name, fn in FRAMES:
        p = os.path.join(GEN, fn)
        if not os.path.exists(p):
            print('нет файла', p)
            continue
        st = stats(p)
        ib = ink_bbox(st)
        print('%-9s %dx%d (%.2f) mean=%s sat=%.2f ochre=%.3f black=%.3f ink=%s'
              % (name, st['w'], st['h'], st['w'] / st['h'], st['mean'], st['sat'],
                 st['ochre'], st['dark'], ib))
        if ib and name.startswith('s1wall'):
            pad = 0.02
            box = (max(0, ib['x0'] - pad), max(0, ib['y0'] - pad),
                   min(1, ib['x1'] + pad), min(1, ib['y1'] + pad))
            crop = st['im'].crop((int(box[0] * st['w']), int(box[1] * st['h']),
                                  int(box[2] * st['w']), int(box[3] * st['h'])))
            cp = os.path.join(SAT, 'crop_%s_ink.png' % name)
            crop.save(cp)
            print('   нативный кроп надписи -> %s (%dx%d)' % (cp, crop.width, crop.height))
        items.append((name, st['im']))
    if items:
        print('лист ->', sheet(items, os.path.join(SAT, 'sheet_s1wall_p6luna.png')))


if __name__ == '__main__':
    main()
