# -*- coding: utf-8 -*-
"""Проверка ровности текстуры: сравнить рендер 0° (лицо) с исходным znachek_k1.png."""
import os
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '_znak3d.py')).read().split("if '--sheet' in sys.argv:")[0]
ns = {'__file__': os.path.join(HERE, '_znak3d.py'), '__name__': 'z3d'}
exec(compile(src, '_znak3d.py', 'exec'), ns)
render = ns['render']

r = np.asarray(render(0)).astype(np.float32)          # 1280x1280
srcimg = Image.open(os.path.join(ns['GEN'], 'znachek_k1.png')).convert('RGB')
# найдём bbox значка в рендере
fg = (np.abs(r - np.array([6, 8, 18])).sum(axis=2) > 24)
ys, xs = np.where(fg)
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
rend = r[y0:y1 + 1, x0:x1 + 1]
# пятиугольник источника: Rp=0.49*S, центр S/2
Sa = np.asarray(srcimg).astype(np.float32)
S = srcimg.width
Rp = 0.49 * S
cx = cy = S / 2
ref = Sa[int(cy - Rp):int(cy + Rp), int(cx - Rp):int(cx + Rp)]
rend_r = np.asarray(Image.fromarray(rend.astype(np.uint8)).resize((ref.shape[1], ref.shape[0]), Image.LANCZOS)).astype(np.float32)
mae = np.abs(rend_r - ref).mean()
print('bbox рендера', x0, x1, y0, y1, '-> w=%d h=%d' % (x1 - x0 + 1, y1 - y0 + 1))
print('MAE рендер vs источник (ниже=ровнее):', round(float(mae), 2))
# контроль середины: центр должен быть светлый/кремовый (лого), не фон
print('центр рендера RGB:', r[640, 640].astype(int).tolist())
print('центр источника RGB:', Sa[int(cy), int(cx)].astype(int).tolist())
# сохраним бок-о-бок для глаза
pair = Image.new('RGB', (ref.shape[1] + rend_r.shape[1] + 20, max(ref.shape[0], rend_r.shape[0])), (10, 10, 14))
pair.paste(Image.fromarray(ref.astype(np.uint8)), (0, 0))
pair.paste(Image.fromarray(rend_r.astype(np.uint8)), (ref.shape[1] + 20, 0))
pair.save(os.path.join(ns['REVIEW'], 'review_51_tex_vs_src.png'))
print('saved review_51_tex_vs_src.png')
