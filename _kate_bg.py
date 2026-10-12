# -*- coding: utf-8 -*-
import os
import numpy as np
from PIL import Image
H = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(H, 'assets', 'gen')
a = np.asarray(Image.open(os.path.join(G, 'kate_overalls_0.png')).convert('RGB'), np.int16)
h, w, _ = a.shape
print('shape', a.shape)
print('corners:', a[0, 0], a[0, -1], a[-1, 0], a[-1, -1])
print('border rows mean:', a[0].mean(0), a[-1].mean(0))
print('border cols mean:', a[:, 0].mean(0), a[:, -1].mean(0))
print('top-left 40x40 min/mean:', a[:40, :40].min(), a[:40, :40].mean())
# гистограмма яркости по границе
mnb = a[0].min(1)
print('top row min-channel: min%d max%d' % (mnb.min(), mnb.max()))
print('unique-ish sample top-left:', a[0, 0], a[0, 30], a[30, 0], a[100, 0], a[0, 100])
