# -*- coding: utf-8 -*-
"""Проверка 16:9-кадров вращения: где значок, насколько узкий на ребре."""
import os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '_znak3d_rot.py')).read().split("if '--frames' in sys.argv:")[0]
ns = {'__file__': os.path.join(HERE, '_znak3d_rot.py'), '__name__': 'rotmod'}
exec(compile(src, '_znak3d_rot.py', 'exec'), ns)
render, angle_at = ns['render'], ns['angle_at']
for tt in (0.0, 2.2, 3.0, 4.0):
    im = np.asarray(render(tt)).astype(int)
    fg = (np.abs(im - np.array([6, 8, 18])).sum(axis=2) > 30)
    cols = np.where(fg.any(axis=0))[0]
    if len(cols):
        c0, c1 = cols.min(), cols.max()
        print('t=%.1f (%3.0f°) ширина=%4d px  центр x=%4d (кадр W=1280, центр 640)'
              % (tt, angle_at(tt), c1 - c0 + 1, (c0 + c1) // 2))
    else:
        print('t=%.1f — пусто' % tt)
