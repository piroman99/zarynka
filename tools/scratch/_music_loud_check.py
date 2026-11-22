# -*- coding: utf-8 -*-
"""Сравнение громкости музыки сцен (RMS/max) — чтобы аллея не играла тише остальных."""
import os
import subprocess

import numpy as np

FF = os.path.abspath(os.path.join('..', '..', '.probe', '.lib', 'imageio_ffmpeg', 'binaries',
                                 'ffmpeg-linux-x86_64-v7.0.2'))
SR = 22050
O = 'assets/audio/sketch/'


def pcm(path):
    raw = subprocess.run([FF, '-hide_banner', '-v', 'error', '-i', path, '-f', 'f32le',
                          '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def db(x):
    return 20 * np.log10(max(float(x), 1e-12))


for f in ['vn_reception_soft_0.mp3', 'prolog_bed_soft_0.mp3', 'alley_mix.mp3', 'alley_bed.mp3']:
    p = O + f
    if not os.path.exists(p):
        print('%-26s нет файла' % f)
        continue
    x = pcm(p)
    print('%-26s RMS %6.1f dBFS  пик %5.2f  %.0f с'
          % (f, db(np.sqrt((x ** 2).mean())), float(np.abs(x).max()), len(x) / SR))
