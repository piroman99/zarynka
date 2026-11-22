# -*- coding: utf-8 -*-
"""Полоса сравнения масштабов поэта: прежний (518), +50%, +60%."""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, '_sat')
BOX = (110, 180, 830, 1080)


def crop(name, scale=0.72):
    im = Image.open(os.path.join(OUT, name)).convert('RGB').crop(BOX)
    return im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)


def main():
    tiles = [('сейчас (518 px, ноги выше ножек)', crop('final_B_full.jpg')),
             ('+50 % (777 px, ноги ниже ножек)', crop('sc150_full.jpg')),
             ('+60 % (828 px)', crop('sc160_full.jpg'))]
    tw, th = tiles[0][1].size
    sh = Image.new('RGB', (tw * 3 + 20, th + 46), (252, 252, 250))
    d = ImageDraw.Draw(sh)
    for i, (lab, t) in enumerate(tiles):
        x = i * (tw + 10)
        sh.paste(t, (x, 40))
        d.text((x + 6, 16), lab, fill=(150, 0, 0) if i == 0 else (0, 90, 20))
    p = os.path.join(OUT, 'SCALE_compare.jpg')
    sh.save(p, quality=93)
    print('saved', os.path.relpath(p, HERE), sh.size, os.path.getsize(p), 'B')

    g = Image.open(os.path.join(OUT, 'sc150_full.jpg')).convert('RGB').crop(BOX)
    g.save(os.path.join(OUT, 'SCALE_guides.jpg'), quality=93)
    print('saved SCALE_guides.jpg', g.size)


if __name__ == '__main__':
    main()
