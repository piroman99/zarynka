# -*- coding: utf-8 -*-
"""Сравнение B (v2 fixed2, доращённая ножка) и C (v4 — новая крашеная).

Геометрия та же, что в одобренном _bench_final.py:
  высота ближнего торца 0.90 м; земля считается от кончика правой передней ножки;
  левый край скамейки на 15 px правее линии бордюра (x = 0.2856*y - 108.5).
Поэт: спрайт 780 px, таз на линии сиденья.
"""
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
W, H = 1920, 1080
Y_H, K = 572.0, 1.146
SLOPE = np.tan(np.radians(23.6))
BACK_H, SEAT_H = 0.90, 0.45
P_BUTT_F = 0.625
POET_H = 780

BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')

CFG = {
    'B v2': dict(path=os.path.join(ROOT, '_sat', 'prop_bench_new_fixed2.png'),
                 near=(137, 880), front=(555, 995), band=60),
    'C v4': dict(path=os.path.join(ROOT, '_sat', 'prop_bench_v4_matte.png'),
                 near=(94, 733), front=(465, 824), band=60),
}


def curb(y):
    return 0.2856 * y - 108.5


def place(cfg, label, x_leg=260.0, y_leg=960.0):
    im = Image.open(cfg['path']).convert('RGBA')
    m = np.asarray(im)[:, :, 3] > 140
    x_near, y_near = cfg['near']
    band = m[:, max(0, x_near - cfg['band']):x_near + 300]
    rows = band.sum(axis=1)
    top = int(np.nonzero(rows > 6)[0].min())
    span = y_near - top
    m_scene = K * (y_leg - Y_H)
    k = (BACK_H * m_scene) / span
    prop = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    paste = (int(round(x_leg - x_near * k)), int(round(y_leg - y_near * k)))
    left = paste[0] + int(np.nonzero((np.asarray(prop)[:, :, 3] > 140).any(axis=0))[0].min())
    print('%s: верх %d, span %d, k=%.4f, файл->%dx%d, левый край %d (бордюр %.0f)'
          % (label, top, span, k, prop.width, prop.height, left, curb(y_leg)))
    return prop, paste, k


def main():
    panels = []
    for label, cfg in CFG.items():
        x = 200.0
        for _ in range(6):
            prop, paste, k = place(cfg, label, x)
            left = paste[0] + int(np.nonzero((np.asarray(prop)[:, :, 3] > 140).any(axis=0))[0].min())
            x += (curb(960.0) + 15 - left)
        prop, paste, k = place(cfg, label, x)

        canvas = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')

        put_kate = Image.open(KATE).convert('RGBA')
        hh = round(H * 99 / 100.0)
        ww = round(put_kate.width * hh / put_kate.height)
        put_kate = put_kate.resize((ww, hh), Image.LANCZOS)
        canvas.alpha_composite(put_kate, (round(W * 73 / 100.0 - ww / 2.0), round(H * 1.03) - hh))
        canvas.alpha_composite(prop, paste)

        m_scene = K * (960.0 - Y_H)
        fx, fy = cfg['front']
        f_screen = (paste[0] + fx * k, paste[1] + fy * k)
        seat_x = paste[0] + cfg['near'][0] * k + 0.295 * 1.8 * m_scene
        ground_y = f_screen[1] - SLOPE * (seat_x - f_screen[0])
        seat_y = ground_y - SEAT_H * m_scene
        poet = Image.open(POET).convert('RGBA')
        pw = round(poet.width * POET_H / poet.height)
        poet = poet.resize((pw, POET_H), Image.LANCZOS)
        canvas.alpha_composite(poet, (int(round(seat_x - pw / 2.0)),
                                      int(round(seat_y - P_BUTT_F * POET_H))))
        # контроль: низ правой передней ножки = земля, таз − доска, левый край
        print('   кончик передней ножки (%.0f, %.0f); сиденье у поэта (%.0f, %.0f), земля %.0f'
              % (f_screen[0], f_screen[1], seat_x, seat_y, ground_y))
        panels.append((label, canvas))

    box = (0, int(H * 0.33), int(W * 0.62), H)
    crops = [c.convert('RGB').crop(box) for _, c in panels]
    cw, ch = crops[0].size
    sh = Image.new('RGB', (cw * 2, ch), (255, 255, 255))
    d = ImageDraw.Draw(sh)
    for i, (lab, _) in enumerate(panels):
        sh.paste(crops[i], (cw * i, 0))
        d.rectangle([cw * i + 10, 10, cw * i + 210, 58], fill=(255, 255, 255))
        d.text((cw * i + 22, 26), lab, fill=(170, 0, 0))
    p = os.path.join(OUT, 'BC_v4.jpg')
    sh.save(p, quality=90)
    print('saved', os.path.relpath(p, HERE), sh.size, os.path.getsize(p), 'B')
    for lab, c in panels:
        q = os.path.join(OUT, 'v4_%s' % ('B' if 'v2' in lab else 'C'))
        c.convert('RGB').save(q + '_full.jpg', quality=90)
        c.convert('RGB').resize((1280, 720), Image.LANCZOS).save(q + '.jpg', quality=88)


if __name__ == '__main__':
    main()
