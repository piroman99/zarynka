# -*- coding: utf-8 -*-
"""Регресс: пакетный дефринж должен дать то же, что уже принятый poet_seat_upset.

Берём ИСХОДНЫЙ файл из git (30f682c — состояние до дефринжа), прогоняем пакетную
функцию и сравниваем с принятым файлом в рабочем дереве.
"""
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

NAME = 'poet_seat_upset.webp'
rel = 'vn2/img/char/' + NAME

orig = subprocess.run(['git', 'show', '30f682c:' + rel], cwd=ROOT, capture_output=True)
print('исходник из git: %d B' % len(orig.stdout))
src = np.asarray(Image.open(io.BytesIO(orig.stdout)).convert('RGBA'))
out = db.defringe(src)

cur = np.asarray(Image.open(os.path.join(ROOT, rel)).convert('RGBA'))
print('принятый файл: %s' % (cur.shape,))

d = np.abs(out.astype(int) - cur.astype(int))
print('сравнение с принятым: RGB max %d, alpha max %d, средний |Δ| %.3f'
      % (d[:, :, :3].max(), d[:, :, 3].max(), d[:, :, :3].mean()))

b = db.edge_stats(src)
a = db.edge_stats(out)
print('до:   кромка %.1f, ядро %.1f, светлых %d' % (b['edge'], b['core'], b['light']))
print('после: кромка %.1f, ядро %.1f, светлых %d' % (a['edge'], a['core'], a['light']))
