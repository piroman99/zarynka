# -*- coding: utf-8 -*-
"""До/после по кромке спрайта: крупные кропы головы/плеча на фоне аллеи."""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, '_sat')
BOX = (250, 240, 560, 560)     # голова и плечо поэта
SCALE = 2.6


def tile(name):
    im = Image.open(os.path.join(OUT, name)).convert('RGB').crop(BOX)
    return im.resize((int(im.width * SCALE), int(im.height * SCALE)), Image.LANCZOS)


def main():
    b = tile('EDGE_before_full.jpg')
    a = tile('EDGE_after_full.jpg')
    tw, th = b.size
    sh = Image.new('RGB', (tw * 2 + 14, th + 44), (252, 252, 250))
    d = ImageDraw.Draw(sh)
    sh.paste(b, (0, 40))
    sh.paste(a, (tw + 14, 40))
    d.text((8, 16), 'было: белая окантовка (кромка 152 против 70 в ядре)', fill=(150, 0, 0))
    d.text((tw + 22, 16), 'стало: кромка 68 против 70', fill=(0, 90, 20))
    p = os.path.join(OUT, 'EDGE_compare.jpg')
    sh.save(p, quality=94)
    print('saved', os.path.relpath(p, HERE), sh.size, os.path.getsize(p), 'B')


if __name__ == '__main__':
    main()
