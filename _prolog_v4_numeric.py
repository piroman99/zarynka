# -*- coding: utf-8 -*-
"""Числовая проверка v4: грейд (R>B), наличие S7-хвоста, затемнение в конце."""
import os, subprocess
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.abspath(os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg',
                                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2'))
TMP = os.path.join(HERE, '.tmp_diag')
SRC = os.path.join(HERE, 'out', 'prolog_animatic_draft.mp4')

TS = [1.0, 2.0, 20.0, 40.0, 60.0, 80.0, 88.5, 90.0, 93.0, 96.5, 97.4]

def frame(t, tag):
    p = os.path.join(TMP, 'num_%s.png' % tag)
    subprocess.run([FF, '-y', '-ss', '%.3f' % t, '-i', SRC, '-frames:v', '1', p],
                   capture_output=True, text=True)
    return np.asarray(Image.open(p).convert('RGB'), np.float32)

print('  t     R     G     B    lum   R-B   R/B')
for t in TS:
    a = frame(t, '%.1f' % t)
    R, G, B = a[..., 0].mean(), a[..., 1].mean(), a[..., 2].mean()
    lum = 0.299 * R + 0.587 * G + 0.114 * B
    print('%5.1f %5.1f %5.1f %5.1f %6.1f %5.1f %5.2f' % (t, R, G, B, lum, R - B, R / max(B, 1e-3)))

# грейд: на «освещённых» кадрах должно быть R > B (тёплый тинт)
print()
a = frame(60.0, 'gradecheck')
print('грейд-чек (t=60): R-B = %.1f (>0 => тёплый)' % (a[..., 0].mean() - a[..., 2].mean()))
# затемнение: t=97.4 почти чёрное
a = frame(97.4, 'blackcheck')
print('финал (t=97.4): средняя яркость = %.1f (близко к 0 => затемнение)' %
      (0.299 * a[..., 0].mean() + 0.587 * a[..., 1].mean() + 0.114 * a[..., 2].mean()))
