# -*- coding: utf-8 -*-
"""Поставить выбранный кадр p6 (лунная станция) мастером: assets/final/prolog/p6.png.

Мастера вставленных кадров p6/p7/p8 лежат «как сгенерированы» (1672x941, без метки
сцены и без грейда) — грейд «тёплый архив» и ресайз делает `_vn2_build.py`.

Выбор варианта — ОДНОЙ строкой (или env P6_PLATE):
    P6_PLATE=p6luna_b__gpt-image-2_0.png python3 _p6_luna_apply.py

Запуск: python3 _p6_luna_apply.py [--dry]
"""
import os
import shutil
import sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
FIN = os.path.join(HERE, 'assets', 'final', 'prolog')

PICK = os.environ.get('P6_PLATE', 'p6luna_a__gpt-image-2_0.jpg')

src = os.path.join(GEN, PICK)
dst = os.path.join(FIN, 'p6.png')

if not os.path.exists(src):
    raise SystemExit('нет файла %s' % src)

im = Image.open(src).convert('RGB')
a = np.asarray(im, np.float32)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
ochre = ((r > 95) & (r > g + 18) & (g > b + 10) & (r - b > 40)).mean()
print('источник %s  %dx%d  mean=%s  охра=%.3f'
      % (PICK, im.width, im.height,
         tuple(round(float(x), 1) for x in a.reshape(-1, 3).mean(0)), ochre))
if ochre > 0.05:
    raise SystemExit('палитра не лунная (охра %.3f) — кадр не ставим' % ochre)
if '--dry' in sys.argv:
    raise SystemExit(0)

if os.path.exists(dst):
    # старый мастер уже в assets/rejected/p6/ (_archive_p6_luna.py)
    print('прежний мастер: %d B' % os.path.getsize(dst))
shutil.copy2(src, dst)
print('p6.png <- %s  (%d B)' % (PICK, os.path.getsize(dst)))
