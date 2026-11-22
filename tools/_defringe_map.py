# -*- coding: utf-8 -*-
"""ASCII-карта региона спрайта: '.' прозрачно, '#' тёмное непрозрачное,
'+' светлое непрозрачное (фон?), 'o' полупрозрачное."""
import io
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load(name, git=False):
    rel = 'vn2/img/char/' + name
    if git:
        raw = subprocess.check_output(['git', 'show', 'HEAD:' + rel], cwd=ROOT)
        return np.asarray(Image.open(io.BytesIO(raw)).convert('RGBA'))
    return np.asarray(Image.open(os.path.join(ROOT, rel)).convert('RGBA'))


def show(arr, x0, x1, y0, y1, step=1):
    sub = arr[y0:y1, x0:x1]
    for y in range(0, sub.shape[0], step):
        row = []
        for x in range(0, sub.shape[1], step):
            r, g, b, a = sub[y, x]
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if a == 0:
                row.append('.')
            elif a < 200:
                row.append('o')
            elif lum > 130:
                row.append('+')
            elif lum > 70:
                row.append('-')
            else:
                row.append('#')
        print('%4d %s' % (y0 + y, ''.join(row)))


name = sys.argv[1]
git = len(sys.argv) > 5
x0, x1, y0, y1 = [int(v) for v in sys.argv[2:6]]
arr = load(name, git)
print('%s %s %dx%d  регион x %d..%d y %d..%d' % (name, 'git' if git else 'work',
                                                 arr.shape[1], arr.shape[0], x0, x1, y0, y1))
show(arr, x0, x1, y0, y1)
