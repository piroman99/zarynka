# -*- coding: utf-8 -*-
"""Сравнение A (доски впуск между стойками) и B (доски снаружи, шляпки винтов)."""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, '_sat')


def load(prefix):
    return Image.open(os.path.join(OUT, prefix + '_full.jpg')).convert('RGB')


def panel(im, box, scale):
    c = im.crop(box)
    return c.resize((int(c.width * scale), int(c.height * scale)), Image.LANCZOS)


def main():
    a, b = load('blend7A'), load('blend7B')
    box_all = (40, 380, 800, 1010)
    box_back = (90, 400, 640, 780)

    pa, pb = panel(a, box_all, 1.0), panel(b, box_all, 1.0)
    za, zb = panel(a, box_back, 1.7), panel(b, box_back, 1.7)

    w = pa.width * 2 + 20
    h = pa.height + za.height + 70
    sh = Image.new('RGB', (w, h), (250, 250, 248))
    d = ImageDraw.Draw(sh)
    sh.paste(pa, (0, 40))
    sh.paste(pb, (pa.width + 20, 40))
    y2 = 40 + pa.height + 20
    sh.paste(za, (0, y2))
    sh.paste(zb, (pa.width + 20, y2))
    d.rectangle([0, 0, 300, 34], fill=(255, 255, 255))
    d.text((8, 12), 'A — доски впуск между стойками', fill=(160, 0, 0))
    d.rectangle([pa.width + 20, 0, pa.width + 320, 34], fill=(255, 255, 255))
    d.text((pa.width + 28, 12), 'B — доски снаружи, винты', fill=(0, 90, 0))
    p = os.path.join(OUT, 'AB_bench_v7.jpg')
    sh.save(p, quality=92)
    print('saved', os.path.relpath(p, HERE), sh.size, os.path.getsize(p), 'B')


if __name__ == '__main__':
    main()
