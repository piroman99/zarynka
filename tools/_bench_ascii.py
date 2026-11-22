# -*- coding: utf-8 -*-
"""ASCII-карта пропа-скамейки: альфа и цвет — чтобы «увидеть» форму без зрения.

Печатаем две сетки 72x26: (1) плотность альфы, (2) средний цвет в клетке
(буквы: G — зелень, W — светлое/бумага, D — тёмное дерево, S — серое).
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))



ROOT = os.path.dirname(HERE)
def grid(path, cols=72, rows=26):
    im = Image.open(path)
    rgba = im.convert('RGBA')
    a = np.asarray(rgba.split()[-1]).astype(np.float32)
    rgb = np.asarray(rgba.convert('RGB')).astype(np.float32)
    H, W = a.shape
    print('\n=== %s  %dx%d' % (os.path.basename(path), W, H))
    alpha_chars = ' .:-=+*#%@'
    lines_a, lines_c = [], []
    for r in range(rows):
        y0, y1 = int(r * H / rows), int((r + 1) * H / rows)
        la, lc = [], []
        for c in range(cols):
            x0, x1 = int(c * W / cols), int((c + 1) * W / cols)
            blk_a = a[y0:y1, x0:x1].mean() / 255.0
            la.append(alpha_chars[min(9, int(blk_a * 9.99))])
            blk = rgb[y0:y1, x0:x1].reshape(-1, 3).mean(0)
            R, G, B = blk
            mx, mn = max(R, G, B), min(R, G, B)
            sat = (mx - mn) / (mx + 1e-6)
            lum = 0.299 * R + 0.587 * G + 0.114 * B
            if sat > 0.18 and G >= R and G >= B:
                ch = 'G' if lum > 90 else 'g'
            elif sat < 0.10 and lum > 190:
                ch = 'W'
            elif lum < 90:
                ch = 'D'
            elif lum > 165:
                ch = 'w'
            else:
                ch = 's'
            if blk_a < 0.10:
                ch = ' '
            lc.append(ch)
        lines_a.append(''.join(la))
        lines_c.append(''.join(lc))
    print('--- альфа ---')
    for ln in lines_a:
        print('|' + ln + '|')
    print('--- цвет (G/g зелень, W/w светлое, D тёмное, s серое) ---')
    for ln in lines_c:
        print('|' + ln + '|')


grid(os.path.join(ROOT, 'vn2', 'img', 'prop', 'bench.webp'))
