# -*- coding: utf-8 -*-
"""Перебор глубины посадки (SINK) — три варианта одной полосой.

Щель под задницей может читаться по-разному: от «висит» до «провалился».
Гоняем 6/18/30 px и складываем крупные кропы рядом, чтобы выбрать глазом.
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, '_sat')
SINKS = [('A', 6), ('B', 18), ('C', 30)]
BOX = (200, 560, 700, 1010)


def run(sink, prefix):
    env = dict(os.environ, SINK=str(sink), PREFIX=prefix)
    r = subprocess.run(['python3', '_alley_final2.py'], cwd=HERE, env=env,
                       capture_output=True, text=True, timeout=600)
    tail = [l for l in r.stdout.strip().splitlines() if 'задница' in l or 'щель' in l or 'фигура' in l]
    print('--- SINK=%d' % sink)
    for l in tail:
        print('   ' + l.strip())
    return os.path.join(OUT, prefix + '_full.jpg')


def main():
    tiles = []
    for name, sink in SINKS:
        p = run(sink, 'sweep' + name)
        im = Image.open(p).convert('RGB').crop(BOX)
        im = im.resize((int(im.width * 1.05), int(im.height * 1.05)), Image.LANCZOS)
        tiles.append(('%s — утопление %d px' % (name, sink), im))

    tw, th = tiles[0][1].size
    sh = Image.new('RGB', (tw * len(tiles) + 12 * (len(tiles) - 1), th + 48), (252, 252, 250))
    d = ImageDraw.Draw(sh)
    for i, (lab, t) in enumerate(tiles):
        x = i * (tw + 12)
        sh.paste(t, (x, 42))
        d.text((x + 6, 18), lab, fill=(140, 0, 0))
    p = os.path.join(OUT, 'SINK_compare.jpg')
    sh.save(p, quality=93)
    print('\nsaved', os.path.relpath(p, HERE), sh.size, os.path.getsize(p), 'B')


if __name__ == '__main__':
    main()
