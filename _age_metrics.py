# -*- coding: utf-8 -*-
"""Объективные метрики «возраста» на лице: морщины лба, текстура щетины.
Лоб: горизонтальные линии -> энергия вертикального градиента |dI/dy|.
Щетина (усы/подбородок): плотность мелкой текстуры (локальное СКО).
Все метрики — в процентах от канона (база = 100 %).
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
V2 = os.path.join(GEN, '_sergey_v2')

FILES = [
    ('база (canon)', os.path.join(GEN, 'sergey_eng_old__flux-2_0.jpg')),
    ('smile OLD', os.path.join(GEN, 'sergey_smile_0.jpg')),
    ('smile flux v2', os.path.join(V2, 'sergey_smile__flux-2_0.jpg')),
    ('smile gpt v2', os.path.join(V2, 'sergey_smile__gpt-image-2_0.png')),
    ('conc OLD', os.path.join(GEN, 'sergey_concerned_0.jpg')),
    ('conc flux v2', os.path.join(V2, 'sergey_concerned__flux-2_0.jpg')),
    ('conc gpt v2', os.path.join(V2, 'sergey_concerned__gpt-image-2_0.png')),
]

# зоны в долях кадра (проверены по базовому спрайту): лоб и щетина
ZONES = {'лоб': (.34, .56, .10, .20),      # x0,x1,y0,y1
         'щетина': (.34, .66, .30, .38)}


def metrics(path):
    im = Image.open(path).convert('L')
    a = np.asarray(im, np.float32)
    out = {}
    for nm, (x0, x1, y0, y1) in ZONES.items():
        h, w = a.shape
        z = a[int(h * y0):int(h * y1), int(w * x0):int(w * x1)]
        if z.size < 100:
            out[nm] = float('nan')
            continue
        gy = np.abs(np.diff(z, axis=0)).mean()      # горизонтальные линии
        gx = np.abs(np.diff(z, axis=1)).mean()
        # локальное СКО (мелкая текстура: щетина)
        k = 5
        m = z[:z.shape[0] // k * k, :z.shape[1] // k * k]
        m = m.reshape(m.shape[0] // k, k, m.shape[1] // k, k).transpose(0, 2, 1, 3)
        sd = m.reshape(-1, k * k).std(1).mean()
        out[nm] = (gy, gx, sd)
    return out


base = metrics(FILES[0][1])
print('%-16s %14s %14s' % ('', 'лоб (gy/100%)', 'щетина (СКО/100%)'))
for label, p in FILES:
    m = metrics(p)
    print('%-16s %14.0f %14.0f' % (label,
                                   100 * m['лоб'][0] / base['лоб'][0],
                                   100 * m['щетина'][2] / base['щетина'][2]))
