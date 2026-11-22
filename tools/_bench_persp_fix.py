# -*- coding: utf-8 -*-
"""Правка перспективы новой скамейки: все четыре ножки — на землю.

Что измерено в `prop_bench_new_matte.png` (1407x996), низ ножек:
    ближняя задняя  (133, 879)   ближняя передняя (555, 995)
    дальняя задняя  (1050, 504)  дальняя передняя (1336, 531)
Требование перспективы: линии низа передних и низа задних ножек параллельны оси аллеи,
т.е. идут в точку схода ворот под 23.6°. Проверка:
    задние:  наклон 22.2°  — почти правильно (дальняя задняя ниже нормы на ~25 px файла);
    передние: наклон 30.7° — дальняя передняя ВЫШЕ нормы на 123 px файла = 62 px на
              экране = 14 см по масштабу сцены. Отсюда «правая сторона взлетела»:
              у скамейки перекошена передняя линия, а задняя стоит почти верно.

Лечение: проективное преобразование по четырём точкам — обе дальние ножки ставятся на
свои правильные линии, ближние остаются на месте. После этого ось пропа уже совпадает
с осью аллеи, поворот не нужен.
"""
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
W, H = 1920, 1080
Y_H, K = 572.0, 1.146
VANISH = (1037.0, 572.0)
BACK_H, SEAT_H = 0.90, 0.45
P_HEAD_F, P_FEET_F, P_BUTT_F = 201 / 1433.0, 1419 / 1433.0, 0.625
POET_H = 780

BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
NEW = os.path.join(ROOT, '_sat', 'prop_bench_new_matte.png')
OLD = os.path.join(ROOT, 'assets', 'sprites', 'prop_bench.png')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')

SLOPE = np.tan(np.radians(23.6))       # наклон оси аллеи в кадре


def curb_x(y):
    return 0.2856 * y - 108.5


def find_coeffs(pa, pb):
    """Коэффициенты для Image.transform(PERSPECTIVE): pa — куда (output), pb — откуда."""
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])
    A = np.array(matrix, dtype=float)
    B = np.array(pb, dtype=float).reshape(8)
    res = np.linalg.solve(A.T @ A, A.T @ B)
    return res.reshape(8)


def fix_perspective():
    im = Image.open(NEW).convert('RGBA')
    Wf, Hf = im.size
    nb, nf, fb, ff = (133.0, 879.0), (555.0, 995.0), (1050.0, 504.0), (1336.0, 531.0)
    fb_t = (fb[0], nb[1] - SLOPE * (fb[0] - nb[0]))     # на линии задних ножек
    ff_t = (ff[0], nf[1] - SLOPE * (ff[0] - nf[0]))     # на линии передних ножек
    print('дальняя задняя: %.0f -> %.0f (%+.0f px файла)', fb[1], fb_t[1], fb_t[1] - fb[1])
    print('дальняя передняя: %.0f -> %.0f (%+.0f px файла)', ff[1], ff_t[1], ff_t[1] - ff[1])
    # порядок обхода важен: контур земли по периметру (ближняя-задняя -> ближняя-передняя
    # -> дальняя-передняя -> дальняя-задняя). В «крестовом» порядке гомография
    # переворачивает всю плоскость и холст заливается непрозрачным.
    src = [nb, nf, ff_t, fb_t]
    dst = [nb, nf, ff, fb]
    coeffs = find_coeffs(src, dst)
    out = im.transform((Wf, Hf), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    out.save(os.path.join(OUT, 'prop_bench_new_fixed.png'))
    return out


def leg_bottom(im, x0, x1):
    a = np.asarray(im)
    m = a[:, :, 3] > 140
    best = (0, 0)
    for x in range(x0, min(x1, m.shape[1])):
        col = np.nonzero(m[:, x])[0]
        if col.size and col.max() > best[1]:
            best = (x, col.max())
    return best


def place(im, label, anchor_x=148.0, anchor_y=960.0, near=(133, 879), vert=(133, 879, 100)):
    """Ставит проп так, чтобы ножка near оказалась в (anchor_x, anchor_y)."""
    a = np.asarray(im)
    m = a[:, :, 3] > 140
    # верх ближнего торца: первая строка, где в полосе рядом с ножкой есть хотя бы 6
    # непрозрачных пикселей (одна случайная точка сверху — артефакт поворота)
    x_leg = vert[0]
    band = m[:, max(0, x_leg - 60):x_leg + 260]
    rows = band.sum(axis=1)
    top = int(np.nonzero(rows > 6)[0].min())
    bot = vert[1]
    span = bot - top
    m_scene = K * (anchor_y - Y_H)
    k = (BACK_H * m_scene) / span
    prop = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    px = int(round(anchor_x - near[0] * k))
    py = int(round(anchor_y - near[1] * k))
    print('%s: верх торца %d, низ %d -> span %d, k=%.4f, проп %dx%d в (%d,%d)'
          % (label, top, bot, span, k, prop.width, prop.height, px, py))
    return prop, (px, py), k


def main():
    fixed = fix_perspective()
    # проверка после правки
    for name, win in (('ближняя задняя', (60, 200)), ('ближняя передняя', (480, 620)),
                      ('дальняя задняя', (990, 1100)), ('дальняя передняя', (1290, 1380))):
        x, y = leg_bottom(fixed, *win)
        print('  после правки %-16s (%4d, %4d)' % (name, x, y))

    panels = []
    for label, im, near, vert in (
            ('A старая', Image.open(OLD).convert('RGBA'), (133, 868), (133, 868, 100)),
            ('B новая', fixed, (133, 879), (133, 879, 100))):
        m_scene = K * (960.0 - Y_H)
        # сдвиг, чтобы левый край пропа встал правее бордюра
        for x_leg in (148.0, 210.0, 260.0, 300.0):
            prop, paste, k = place(im, '%s probe X=%.0f' % (label, x_leg), x_leg, 960.0, near, vert)
            left = paste[0] + int(np.nonzero((np.asarray(prop)[:, :, 3] > 140).any(axis=0))[0].min())
            if left > curb_x(960.0) + 10:
                break
        print('   -> X=%.0f: левый край %d (бордюр %.0f)' % (x_leg, left, curb_x(960.0)))

        canvas = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')

        def put(c, p, left_pct=73.0, height_pct=99.0, bottom_pct=-3.0):
            i2 = Image.open(p).convert('RGBA')
            h = round(H * height_pct / 100.0)
            w = round(i2.width * h / i2.height)
            i2 = i2.resize((w, h), Image.LANCZOS)
            c.alpha_composite(i2, (round(W * left_pct / 100.0 - w / 2.0),
                                   round(H * (1.0 - bottom_pct / 100.0)) - h))

        put(canvas, KATE, 73, 99, -3)
        canvas.alpha_composite(prop, paste)

        # земля у передней ножки в кадре: ближняя передняя + та же линия
        nf = (555, 995) if 'новая' in label else (520, 972)
        nf_scene = (paste[0] + nf[0] * k, paste[1] + nf[1] * k)
        along = 0.295 * 1.8 * m_scene
        seat_x = paste[0] + near[0] * k + along
        ground_y = nf_scene[1] - SLOPE * (seat_x - nf_scene[0])
        seat_y = ground_y - SEAT_H * m_scene
        print('   сиденье у поэта (%.0f, %.0f), земля там %.0f' % (seat_x, seat_y, ground_y))

        poet = Image.open(POET).convert('RGBA')
        pw = round(poet.width * POET_H / poet.height)
        poet = poet.resize((pw, POET_H), Image.LANCZOS)
        px = int(round(seat_x - pw / 2.0))
        py = int(round(seat_y - P_BUTT_F * POET_H))
        canvas.alpha_composite(poet, (px, py))
        panels.append((label, canvas, x_leg, left))

    box = (0, int(H * 0.33), int(W * 0.62), H)
    crops = [c.convert('RGB').crop(box) for _, c, _, _ in panels]
    cw, ch = crops[0].size
    sh = Image.new('RGB', (cw * 2, ch), (255, 255, 255))
    d = ImageDraw.Draw(sh)
    for i, (lab, _, x, left) in enumerate(panels):
        sh.paste(crops[i], (cw * i, 0))
        d.rectangle([cw * i + 10, 10, cw * i + 460, 58], fill=(255, 255, 255))
        d.text((cw * i + 20, 26), '%s  ножка X=%.0f, край %d' % (lab, x, left), fill=(170, 0, 0))
    p = os.path.join(OUT, 'AB_fixed.jpg')
    sh.save(p, quality=90)
    print('saved', os.path.relpath(p, HERE), sh.size, os.path.getsize(p), 'B')


if __name__ == '__main__':
    main()
