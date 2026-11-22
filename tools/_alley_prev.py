# -*- coding: utf-8 -*-
"""Превью сцены «аллея» на НОВОМ фоне (без нарисованной скамейки).

Собирает то же, что движок, но без браузера: 1920x1080, фон + статичный проп
(скамейка) + сидящий поэт и Екатерина. Геометрия берётся ИЗ КОНСТАНТ движка:
  .sprite        bottom:-3%  height:99%   slot0 left:27%  slot1 left:73%
  .sprite.seated height:88%
  #props .prop   bottom:-3%  height:40% (в узле: left 41%, bottom -10.8%, h 72%)
Низ кадра у CSS-элемента = bottom:N% от 1080; элемент масштабируется по высоте,
ширина — пропорционально (width:auto, object-fit:contain).

Кладёт три файла:
  _sat/alley_prev_full.jpg   — весь кадр 1920x1080
  _sat/alley_prev_x2.jpg     — кадр с двухкратным увеличением центральной зоны
  _sat/alley_prev.jpg        — сжатое превью 1280x720 для отправки
Плюс печатает числа: bbox пропа и поэта, линия бёдер, где стоят ножки.
"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
W, H = 1920, 1080

BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
PROP = os.path.join(ROOT, 'vn2', 'img', 'prop', 'bench.webp')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')
os.makedirs(OUT, exist_ok=True)


def place_el(canvas, path, left_pct=None, bottom_pct=-3.0, height_pct=88.0, center_left=False):
    """Ставит PNG/WEBP по правилам CSS движка. Возвращает bbox (l,t,r,b)."""
    im = Image.open(path).convert('RGBA')
    h = round(H * height_pct / 100.0)
    w = round(im.width * h / im.height)
    im = im.resize((w, h), Image.LANCZOS)
    bottom_px = H * (1.0 - bottom_pct / 100.0)   # bottom:-3% -> низ ниже края
    top = round(bottom_px) - h
    if left_pct is not None:
        x = W * left_pct / 100.0
        left = round(x - w / 2.0) if center_left else round(x)
    else:
        left = 0
    canvas.alpha_composite(im, (left, top))
    return (left, top, left + w, top + h)


def main():
    bg = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')
    print('bg:', os.path.basename(BG), Image.open(BG).size, '->', (W, H))

    # Порядок как в DOM движка: фон -> #props (z-index 1) -> #cast (z-index 2).
    kate_bb = place_el(bg, KATE, left_pct=73, bottom_pct=-3, height_pct=99, center_left=True)
    # ВАЖНО: #props .prop имеет transform:translateX(-50%), т.е. left = ЦЕНТР пропа.
    prop_bb = place_el(bg, PROP, left_pct=41, bottom_pct=-10.8, height_pct=72, center_left=True)
    poet_bb = place_el(bg, POET, left_pct=27, bottom_pct=-3, height_pct=88, center_left=True)

    print('prop  bbox l,t,r,b =', prop_bb, ' w x h =', prop_bb[2] - prop_bb[0], prop_bb[3] - prop_bb[1])
    print('poet  bbox l,t,r,b =', poet_bb, ' w x h =', poet_bb[2] - poet_bb[0], poet_bb[3] - poet_bb[1])
    print('kate  bbox l,t,r,b =', kate_bb)

    out_full = os.path.join(OUT, 'alley_prev_full.jpg')
    bg.convert('RGB').save(out_full, quality=90)
    print('saved', os.path.relpath(out_full, HERE), os.path.getsize(out_full), 'B')

    # двухкратное увеличение зоны скамейки
    x0 = max(0, prop_bb[0] - 120); x1 = min(W, prop_bb[2] + 120)
    y0 = max(0, prop_bb[1] - 200); y1 = min(H, prop_bb[3] + 60)
    crop = bg.crop((x0, y0, x1, y1)).resize(((x1 - x0) * 2, (y1 - y0) * 2), Image.LANCZOS)
    p2 = os.path.join(OUT, 'alley_prev_x2.jpg')
    crop.convert('RGB').save(p2, quality=90)
    print('saved', os.path.relpath(p2, HERE), crop.size, os.path.getsize(p2), 'B')

    small = bg.convert('RGB').resize((1280, 720), Image.LANCZOS)
    p3 = os.path.join(OUT, 'alley_prev.jpg')
    small.save(p3, quality=88)
    print('saved', os.path.relpath(p3, HERE), os.path.getsize(p3), 'B')


if __name__ == '__main__':
    main()
