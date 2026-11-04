# -*- coding: utf-8 -*-
"""Мерка головы/роста по сырым эмоциям поэта: насколько gpt «уплыл» между эмоциями.

голова/bboxH — главный инвариант (у Сергея 0.340 у всех трёх эмоций, у Кати 0.43–0.45).
Если у поэта разброс большой, одна эмоция «крупнее» другой и в движке будет прыжок.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')

NAMES = ['poet2_b_0.png', 'poet_ha_neutral', 'poet_ha_interested', 'poet_ha_upset',
         'poet_sh_neutral', 'poet_sh_tired', 'poet_sh_inspired']


def find(n):
    if n.endswith('.png'):
        return os.path.join(GEN, n)
    for ext in ('.png', '.jpg'):
        p = os.path.join(GEN, n + '_0' + ext)
        if os.path.exists(p):
            return p
    return None


rows = []
for n in NAMES:
    p = find(n)
    a = np.asarray(Image.open(p).convert('RGB'), np.int16)
    h, w, _ = a.shape
    ring = np.concatenate([a[:8].reshape(-1, 3), a[:h * 3 // 5, :8].reshape(-1, 3),
                           a[:h * 3 // 5, -8:].reshape(-1, 3)])
    seed = np.median(ring, 0)
    m = np.sqrt(((a - seed) ** 2).sum(2)) > 40      # всё, что не фон
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    bh, bw = y1 - y0, x1 - x0
    head = m[y0:y0 + max(4, int(bh * 0.30))]
    hx = np.nonzero(head.any(0))[0]
    hw = int(hx.max() - hx.min())
    rows.append((n, hw, bh, hw / bh))
    print('%-22s голова %4d  рост %4d  голова/рост %.3f' % (n, hw, bh, hw / bh))

rs = [r[3] for r in rows[1:]]
print('\nпо эмоциям (без базы): голова/рост min %.3f max %.3f медиана %.3f разброс %.1f%%'
      % (min(rs), max(rs), float(np.median(rs)), 100 * (max(rs) - min(rs)) / float(np.median(rs))))
