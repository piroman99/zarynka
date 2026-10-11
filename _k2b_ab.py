# -*- coding: utf-8 -*-
"""A/B: кадр с гравировкой vs без — показываем, что штамп реально нарисован."""
import os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '_intro_k2b.py')).read().split("if '--sheet' in sys.argv:")[0]
ns = {'__file__': os.path.join(HERE, '_intro_k2b.py'), '__name__': 'k2bmod'}
exec(compile(src, '_intro_k2b.py', 'exec'), ns)
render = ns['render']
a = np.asarray(render(int(2.45 * 25))).astype(int)
ns['draw_rib_engraving'] = lambda *a, **k: None
# render замкнул draw_rib_engraving? нет — глобальный поиск. Проверим через перезагрузку.
src2 = src.replace('draw_rib_engraving(layer, sx, H / 2, zn.height * 0.80, wpx)',
                   'pass  # engraving OFF')
ns2 = {'__file__': os.path.join(HERE, '_intro_k2b.py'), '__name__': 'k2bmod2'}
exec(compile(src2, '_intro_k2b.py', 'exec'), ns2)
b = np.asarray(ns2['render'](int(2.45 * 25))).astype(int)
diff = (np.abs(a - b).sum(axis=2) > 12)
print('пикселей, изменённых гравировкой:', int(diff.sum()))
ys, xs = np.where(diff)
if len(xs):
    print('bbox x[%d..%d] y[%d..%d]' % (xs.min(), xs.max(), ys.min(), ys.max()))
# сохраним вырезку разницы вокруг ребра
from PIL import Image
crop = np.asarray(ns['render'](int(2.45 * 25)))[:, 860:1060]
Image.fromarray(crop).save(os.path.join(ns['REVIEW'], 'review_42_rib_col.png'))
print('saved review_42_rib_col.png', crop.shape)
