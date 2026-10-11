# -*- coding: utf-8 -*-
"""Ориентация текстуры: сравниваем рендер 0° с источником и его поворотами/зеркалами.
Побеждает минимальный MAE (после выравнивания яркости)."""
import os
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '_znak3d.py')).read().split("if '--sheet' in sys.argv:")[0]
ns = {'__file__': os.path.join(HERE, '_znak3d.py'), '__name__': 'z3d'}
exec(compile(src, '_znak3d.py', 'exec'), ns)
render = ns['render']

r = np.asarray(render(0)).astype(np.float32)
fg = (np.abs(r - np.array([6, 8, 18])).sum(axis=2) > 24)
ys, xs = np.where(fg)
rend = r[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

srcimg = Image.open(os.path.join(ns['GEN'], 'znachek_k1.png')).convert('RGB')
Sa = np.asarray(srcimg).astype(np.float32)
S = srcimg.width; Rp = 0.49 * S; cx = cy = S / 2
ref = Sa[int(cy - Rp):int(cy + Rp), int(cx - Rp):int(cx + Rp)]
H, W = ref.shape[:2]
rend_r = np.asarray(Image.fromarray(rend.astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(np.float32)


def mae_norm(a, b):
    a = a.reshape(-1, 3); b = b.reshape(-1, 3)
    k = float((a * b).sum() / ((a * a).sum() + 1e-6))     # выравнивание яркости
    return float(np.abs(a * k - b).mean())


print('=== сравнение ориентации (MAE после выравнивания яркости) ===')
cands = {
    'как есть': np.asarray(Image.fromarray(rend.astype(np.uint8)).resize((W, H), Image.LANCZOS)),
    'поворот 90': np.asarray(Image.fromarray(rend.astype(np.uint8)).resize((W, H), Image.LANCZOS).rotate(90)),
    'поворот 180': np.asarray(Image.fromarray(rend.astype(np.uint8)).resize((W, H), Image.LANCZOS).rotate(180)),
    'поворот 270': np.asarray(Image.fromarray(rend.astype(np.uint8)).resize((W, H), Image.LANCZOS).rotate(270)),
    'зеркало гориз': np.asarray(Image.fromarray(rend.astype(np.uint8)).resize((W, H), Image.LANCZOS).transpose(Image.FLIP_LEFT_RIGHT)),
    'зеркало верт': np.asarray(Image.fromarray(rend.astype(np.uint8)).resize((W, H), Image.LANCZOS).transpose(Image.FLIP_TOP_BOTTOM)),
}
res = {}
for name, im in cands.items():
    m = mae_norm(np.asarray(im).astype(np.float32), ref)
    res[name] = m
for name, m in sorted(res.items(), key=lambda kv: kv[1]):
    print('  %-16s MAE=%.2f %s' % (name, m, '  <-- лучше' if m == min(res.values()) else ''))
