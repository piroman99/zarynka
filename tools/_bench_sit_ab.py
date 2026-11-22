# -*- coding: utf-8 -*-
"""До/после: поэт висел (спрайт 780 px, таз на 0.625 файла) и сел по замеру."""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, '_sat')
BOX = (60, 380, 900, 1050)


def crop(path, scale=0.95):
    im = Image.open(os.path.join(OUT, path)).convert('RGB').crop(BOX)
    return im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)


def main():
    before = crop('wc_B_full.jpg')
    after = crop('sit_B_h132_full.jpg')
    tw, th = before.size
    sh = Image.new('RGB', (tw * 2 + 16, th + 44), (252, 252, 250))
    d = ImageDraw.Draw(sh)
    sh.paste(before, (0, 40))
    sh.paste(after, (tw + 16, 40))
    d.text((8, 16), 'было: поэт висел ~20 см над доской', fill=(150, 0, 0))
    d.text((tw + 24, 16), 'стало:', fill=(0, 90, 20))
    p = os.path.join(OUT, 'SIT_before_after.jpg')
    sh.save(p, quality=93)
    print('saved', os.path.relpath(p, HERE), sh.size, os.path.getsize(p), 'B')

    full = Image.open(os.path.join(OUT, 'sit_B_h132_full.jpg')).convert('RGB')
    full.resize((1280, 720), Image.LANCZOS).save(os.path.join(OUT, 'SIT_full.jpg'), quality=89)
    z = full.crop((140, 330, 700, 900))
    z = z.resize((int(z.width * 1.9), int(z.height * 1.9)), Image.LANCZOS)
    z.save(os.path.join(OUT, 'SIT_zoom.jpg'), quality=94)
    print('saved SIT_full.jpg и SIT_zoom.jpg', z.size)


if __name__ == '__main__':
    main()
