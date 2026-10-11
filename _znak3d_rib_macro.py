# -*- coding: utf-8 -*-
"""Макро ребра при 90° (проверка ориентации гравировки на боковой грани)."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
ns = {'__file__': os.path.join(HERE, '_znak3d.py'), '__name__': 'z3d'}
exec(compile(open(os.path.join(HERE, '_znak3d.py')).read().split("if '--sheet' in sys.argv:")[0], '_znak3d.py', 'exec'), ns)
render, REVIEW = ns['render'], ns['REVIEW']
im = render(90)
arr = np.asarray(im)
fg = (np.abs(arr.astype(int) - np.array([6, 8, 18])).sum(axis=2) > 24)
ys, xs = np.where(fg)
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
print('ребро bbox', x0, x1, y0, y1, '-> w=%d h=%d' % (x1 - x0 + 1, y1 - y0 + 1))
crop = im.crop((max(0, x0 - 40), max(0, y0 - 20), min(1280, x1 + 40), min(1280, y1 + 20)))
crop = crop.resize((crop.width * 3, crop.height * 3), Image.NEAREST)
crop.save(os.path.join(REVIEW, 'review_52_rib90_macro.png'))
print('saved review_52_rib90_macro.png', crop.size)
