# -*- coding: utf-8 -*-
"""Полоса сравнения: без обработки | вариант A | вариант B (крупные кропы кадра)."""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, '_sat')
BOX = (150, 560, 640, 900)      # вокруг скамейки, как в *_bench_zoom.jpg
SCALE = 1.55
LABELS = [('wc_0', 'без обработки (Blender)'), ('wc_A', 'A — мягче'), ('wc_B', 'B — акварельнее')]


def main():
    tiles = []
    for prefix, label in LABELS:
        im = Image.open(os.path.join(OUT, prefix + '_full.jpg')).convert('RGB')
        c = im.crop(BOX)
        c = c.resize((int(c.width * SCALE), int(c.height * SCALE)), Image.LANCZOS)
        tiles.append((label, c))

    tw, th = tiles[0][1].size
    pad = 12
    sh = Image.new('RGB', (tw * 3 + pad * 2, th + 46), (252, 252, 250))
    d = ImageDraw.Draw(sh)
    for i, (label, t) in enumerate(tiles):
        x = i * (tw + pad)
        sh.paste(t, (x, 40))
        d.text((x + 6, 16), label, fill=(120, 0, 0) if i == 0 else (0, 80, 20))
    p = os.path.join(OUT, 'WC_compare.jpg')
    sh.save(p, quality=92)
    print('saved', os.path.relpath(p, HERE), sh.size, os.path.getsize(p), 'B')


if __name__ == '__main__':
    main()
