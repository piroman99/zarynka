# -*- coding: utf-8 -*-
"""До/после: прошлая посадка (H=524, земля по низу пропа) и нынешняя (земля под сиденьем)."""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, '_sat')
BOX = (120, 280, 820, 1010)


def crop(name, scale=0.9):
    im = Image.open(os.path.join(OUT, name)).convert('RGB').crop(BOX)
    return im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)


def main():
    before = crop('sit_B_h132_full.jpg')
    after = crop('final_B_full.jpg')
    tw, th = before.size
    sh = Image.new('RGB', (tw * 2 + 16, th + 46), (252, 252, 250))
    d = ImageDraw.Draw(sh)
    sh.paste(before, (0, 40))
    sh.paste(after, (tw + 16, 40))
    d.text((8, 16), 'было: земля = низ пропа (960) -> фигура 1.6 м, ноги в асфальте', fill=(150, 0, 0))
    d.text((tw + 24, 16), 'стало: земля под сиденьем (905)', fill=(0, 90, 20))
    p = os.path.join(OUT, 'SIT2_before_after.jpg')
    sh.save(p, quality=93)
    print('saved', os.path.relpath(p, HERE), sh.size, os.path.getsize(p), 'B')

    g = Image.open(os.path.join(OUT, 'final_guides_full.jpg')).convert('RGB').crop(BOX)
    g = g.resize((int(g.width * 0.95), int(g.height * 0.95)), Image.LANCZOS)
    g.save(os.path.join(OUT, 'SIT2_guides.jpg'), quality=93)
    print('saved SIT2_guides.jpg', g.size)


if __name__ == '__main__':
    main()
