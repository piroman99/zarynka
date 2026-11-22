# -*- coding: utf-8 -*-
"""Где именно расходится RGB: проверяем, что только в прозрачных пикселях."""
import io
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import _defringe_batch as db  # noqa: E402

rel = 'vn2/img/char/poet_seat_upset.webp'
orig = subprocess.run(['git', 'show', '30f682c:' + rel], cwd=ROOT, capture_output=True).stdout
src = np.asarray(Image.open(io.BytesIO(orig)).convert('RGBA'))
out = db.defringe(src)
cur = np.asarray(Image.open(os.path.join(ROOT, rel)).convert('RGBA'))

d = np.abs(out.astype(int) - cur.astype(int)).max(axis=2)
al = cur[:, :, 3]
for lo, hi, lab in ((1, 255, 'альфа > 0'), (128, 255, 'альфа > 128'), (250, 255, 'альфа > 250')):
    m = (al >= lo) & (al <= hi)
    print('%-12s пикселей %7d, |Δ| max %3d, средний %.3f, >0: %d'
          % (lab, m.sum(), d[m].max() if m.any() else -1,
             d[m].mean() if m.any() else -1, (d[m] > 0).sum()))
m0 = al == 0
print('альфа = 0: пикселей %d, |Δ| max %d (цвет там не виден)' % (m0.sum(), d[m0].max() if m0.any() else -1))
