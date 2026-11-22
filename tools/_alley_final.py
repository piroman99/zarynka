# -*- coding: utf-8 -*-
"""Сборка кадра «аллея» с посадкой поэта по замеренным параметрам.

Все числа берутся из _sat/poet_params.json (результат _poet_measure.py):
  px, py        вставка пропа (скамейки)
  seat_frame    экранный y верхней плоскости доски
  ground        экранный y земли под ногами сидящего (низ пропа = контакт ножек)
  f_seat        доля файла спрайта, где силуэт сливается (таз)
  f_feet        доля файла спрайта внизу силуэта (ступни)
  h_px          высота спрайта
  top           экранный y верха спрайта
"""
import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
W, H_IMG = 1920, 1080
BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')
PROP = os.path.join(ROOT, '_sat', 'wc', os.environ.get('PROP', 'prop_B.png'))
PREFIX = os.environ.get('PREFIX', 'final_B')
GUIDES = os.environ.get('GUIDES', '0') == '1'


def main():
    with open(os.path.join(OUT, 'poet_params.json')) as f:
        p = json.load(f)
    print('параметры:', {k: p[k] for k in ('px', 'py', 'seat_frame', 'ground', 'h_px', 'top')})

    prop = Image.open(PROP).convert('RGBA')
    canvas = Image.open(BG).convert('RGB').resize((W, H_IMG), Image.LANCZOS).convert('RGBA')

    kate = Image.open(KATE).convert('RGBA')
    kh = round(H_IMG * 0.99)
    kw = round(kate.width * kh / kate.height)
    kate = kate.resize((kw, kh), Image.LANCZOS)
    canvas.alpha_composite(kate, (round(W * 0.73 - kw / 2.0), round(H_IMG * 1.03) - kh))

    pa = np.asarray(prop)[:, :, 3]
    rows = np.nonzero((pa > 60).any(axis=1))[0]

    # контактная тень скамейки
    flat = prop.split()[3].resize((prop.width, max(1, int(prop.height * 0.16))),
                                  Image.LANCZOS).filter(ImageFilter.GaussianBlur(9))
    shadow = Image.new('RGBA', flat.size, (34, 42, 36, 0))
    shadow.putalpha(flat.point(lambda v: int(v * 0.42)))
    canvas.alpha_composite(shadow, (p['px'], p['py'] + rows.max() - flat.size[1] // 2))

    canvas.alpha_composite(prop, (p['px'], p['py']))

    poet = Image.open(POET).convert('RGBA')
    h_px = int(round(p['h_px']))
    w_px = max(1, round(poet.width * h_px / poet.height))
    poet = poet.resize((w_px, h_px), Image.LANCZOS)
    pl = p['x_poet'] - w_px // 2
    canvas.alpha_composite(poet, (pl, p['top']))

    # тень поэта на доске/земле
    ps = poet.split()[3].resize((w_px, max(1, int(h_px * 0.10))), Image.LANCZOS)
    ps = ps.filter(ImageFilter.GaussianBlur(7))
    psh = Image.new('RGBA', ps.size, (30, 36, 32, 0))
    psh.putalpha(ps.point(lambda v: int(v * 0.34)))
    canvas.alpha_composite(psh, (pl, p['ground'] - ps.size[1] // 2))

    # ---- контроль контактов (по пикселям финального кадра) ----
    cb = np.asarray(canvas)
    bench_mask = np.zeros((H_IMG, W), bool)
    bench_mask[p['py']:p['py'] + prop.height, p['px']:p['px'] + prop.width] = pa > 60

    pa_poet = np.asarray(poet)[:, :, 3] > 60
    poet_mask = np.zeros((H_IMG, W), bool)
    y0, x0 = p['top'], pl
    poet_mask[y0:y0 + poet.height, x0:x0 + poet.width] = pa_poet

    inter = bench_mask & poet_mask
    print('пересечение силуэтов поэта и скамейки: %d px' % inter.sum())

    # насколько таз лежит на доске: ищем в колонках поэта верхнюю границу доски
    seat_y = p['seat_frame']
    test = poet_mask & np.abs(np.arange(H_IMG)[:, None] - seat_y).__le__(3)
    print('поэт в пределах ±3 px от линии доски: %d px' % test.sum())

    bottom = np.nonzero(poet_mask.any(axis=1))[0].max()
    print('низ силуэта поэта %d, земля %d (дельта %+d)' % (bottom, p['ground'], bottom - p['ground']))

    if GUIDES:
        d = ImageDraw.Draw(canvas)
        d.line([(0, seat_y), (W, seat_y)], fill=(255, 0, 200), width=3)
        d.line([(0, p['ground']), (W, p['ground'])], fill=(0, 200, 255), width=3)
        d.line([(0, p['top'] + int(p['f_seat'] * h_px)), (W, p['top'] + int(p['f_seat'] * h_px))],
               fill=(255, 160, 0), width=2)

    full = canvas.convert('RGB')
    full.save(os.path.join(OUT, PREFIX + '_full.jpg'), quality=90)
    full.resize((1280, 720), Image.LANCZOS).save(os.path.join(OUT, PREFIX + '.jpg'), quality=88)
    z = full.crop((140, 260, 760, 1010))
    z.save(os.path.join(OUT, PREFIX + '_zoom.jpg'), quality=94)
    print('saved', PREFIX + '*.jpg', z.size)


if __name__ == '__main__':
    main()
