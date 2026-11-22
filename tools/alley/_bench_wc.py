# -*- coding: utf-8 -*-
"""Акварельная обработка блендер-рендера — локально, PIL+numpy, 0 ₽.

Что делает (всё честно измеримо):
  1) median + лёгкий blur        — снимает «3D-глянец» и резкие рёбра
  2) адаптивное квантование      — плоские заливки вместо градиентов
  3) затемнение по краю (wet edge) — краска копится у контура, главный признак акварели
  4) мягкий «потёк» за контуром   — полупрозрачный ореол цвета вне силуэта
  5) зерно бумаги                 — детерминированный шум, только по маске
Вывод: _sat/wc/prop_<VAR>.png (RGBA в конечном масштабе кадра).
"""
import os

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, '_sat', 'blend', 'bench8.png')
OUT = os.path.join(ROOT, '_sat', 'wc')
os.makedirs(OUT, exist_ok=True)

S_RENDER = 0.29200           # масштаб посадки в кадр (из _bench_compose2.py)
PROP_W = 876                 # конечный размер пропа в кадре (1920x1080)

VARIANTS = {
    'A': dict(median=3, colors=24, edge=0.07, rim=0.09, alpha_blur=1.2, grain=0.018, bleed=0.12),
    'B': dict(median=5, colors=12, edge=0.15, rim=0.17, alpha_blur=2.0, grain=0.034, bleed=0.30),
}


def load_prop():
    im = Image.open(SRC).convert('RGBA')
    w = PROP_W
    h = max(1, round(im.height * (w / float(im.width))))
    return im.resize((w, h), Image.LANCZOS)


def paper_grain(shape, seed=7, blur=1.6):
    rng = np.random.default_rng(seed)
    n = rng.normal(0.0, 1.0, shape).astype(np.float32)
    g = Image.fromarray(((n * 40) + 128).clip(0, 255).astype(np.uint8), 'L')
    g = g.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(g).astype(np.float32)
    a = (a - a.mean())
    a /= (np.abs(a).max() + 1e-6)
    return a


def wet_edge(alpha, strength):
    """тёмное ребро сразу ВНУТРИ контура: градиент размытой альфы."""
    a = np.asarray(alpha.filter(ImageFilter.GaussianBlur(1.4)), dtype=np.float32) / 255.0
    gy, gx = np.gradient(a)
    g = np.sqrt(gx * gx + gy * gy)
    g /= (g.max() + 1e-6)
    inside = (np.asarray(alpha, dtype=np.float32) / 255.0) > 0.35
    rim = np.where(inside, g, 0.0)
    rim /= (rim.max() + 1e-6)
    return 1.0 - strength * np.clip(rim * 2.2, 0.0, 1.0)


def bleed_halo(im, alpha, amount):
    """полупрозрачный ореол цвета за контуром — «краска расплылась по бумаге»."""
    rgb = np.asarray(im.convert('RGB'), dtype=np.float32)
    a = np.asarray(alpha, dtype=np.float32) / 255.0
    # цвет внутри силуэта, размазанный далеко наружу
    src = (rgb * a[..., None])
    num = np.asarray(Image.fromarray(np.clip(src, 0, 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(6)), dtype=np.float32)
    den = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(6)), dtype=np.float32) / 255.0
    col = num / np.maximum(den[..., None], 1e-3)
    halo_a = np.asarray(alpha.filter(ImageFilter.GaussianBlur(5)), dtype=np.float32) / 255.0
    halo_a = np.clip(halo_a - a, 0.0, 1.0) * amount
    out = np.dstack([np.clip(col, 0, 255), halo_a * 255.0])
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


def process(im, p):
    alpha0 = im.split()[3]

    # 1) убрать 3D-резкость
    rgb = im.convert('RGB').filter(ImageFilter.MedianFilter(p['median']))
    rgb = rgb.filter(ImageFilter.GaussianBlur(0.6))

    # 2) плоские заливки
    q = rgb.quantize(colors=p['colors'], method=Image.MEDIANCUT, dither=Image.NONE)
    rgb = q.convert('RGB')
    rgb = rgb.filter(ImageFilter.GaussianBlur(0.5))

    arr = np.asarray(rgb, dtype=np.float32)

    # 3) wet edge — краска у контура темнее
    arr *= wet_edge(alpha0, p['rim'])[..., None]

    # 4) зерно бумаги
    g = paper_grain(arr.shape[:2], seed=11, blur=1.5)
    a = np.asarray(alpha0, dtype=np.float32) / 255.0
    arr *= (1.0 + p['grain'] * g * np.clip(a * 1.6, 0, 1))[..., None]

    # 5) мягкий контур
    alpha = alpha0.filter(ImageFilter.GaussianBlur(p['alpha_blur']))

    # 6) общая «прозрачность» акварели: светлее на 4%
    arr = np.clip(arr * 1.0, 0, 255)

    body = Image.fromarray(np.dstack([arr.clip(0, 255), np.asarray(alpha)]).astype(np.uint8), 'RGBA')

    # 7) ореол-потёк под телом
    if p['bleed'] > 0:
        halo = bleed_halo(rgb, alpha0, p['bleed'])
        canvas = Image.new('RGBA', im.size, (0, 0, 0, 0))
        canvas.alpha_composite(halo)
        canvas.alpha_composite(body)
        body = canvas

    # 8) контурная обводкa тонкая (карандаш) — только по внешнему краю
    if p['edge'] > 0:
        e = alpha0.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(0.8))
        ea = np.asarray(e, dtype=np.float32) / 255.0
        ea = np.clip(ea * 3.0, 0, 1) * p['edge']
        ink = Image.new('RGBA', im.size, (48, 58, 52, 0))
        ink.putalpha(Image.fromarray((ea * 255).astype(np.uint8)))
        canvas = body.copy()
        canvas.alpha_composite(ink)
        body = canvas
    return body


def stats(im, label):
    arr = np.asarray(im)
    a = arr[:, :, 3] > 140
    rgb = arr[:, :, :3][a].astype(np.float32)
    uniq = len(np.unique(arr[:, :, :3][a].reshape(-1, 3), axis=0))
    lum = 0.299 * rgb[:, 0] + 0.587 * rgb[:, 1] + 0.114 * rgb[:, 2]
    g = np.asarray(im.convert('L').filter(ImageFilter.FIND_EDGES), dtype=np.float32)
    print('%-8s размер %dx%d  цветов %6d  ярк ср %.1f  резкость %.2f'
          % (label, im.width, im.height, uniq, lum.mean(), g[a].mean()))


def main():
    im = load_prop()
    print('исходный проп', im.size)
    stats(im, 'рендер')
    paths = {}
    for name, p in VARIANTS.items():
        out = process(im, p)
        path = os.path.join(OUT, 'prop_%s.png' % name)
        out.save(path)
        stats(out, name)
        paths[name] = path
        print('  saved', os.path.relpath(path, HERE), os.path.getsize(path), 'B')
    return paths


if __name__ == '__main__':
    main()
