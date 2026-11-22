# -*- coding: utf-8 -*-
"""Есть ли в миксе улица: доля энергии >5 кГц по секундам (без выравнивания фаз)."""
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


def hf_db_per_sec(x, k=SR * 2):
    out = []
    for i in range(0, min(len(x), 60 * SR) - k, k):
        seg = x[i:i + k] * np.hanning(k)
        sp = np.abs(np.fft.rfft(seg)) ** 2
        f = np.fft.rfftfreq(k, 1 / SR)
        hf = sp[f > 5000].sum()
        tot = sp.sum() + 1e-20
        out.append(10 * np.log10(hf / tot + 1e-20))
    return out


bed = pcm(O + 'alley_bed.mp3')
mix = pcm(O + 'alley_mix.mp3')
a = hf_db_per_sec(bed)
b = hf_db_per_sec(mix)
n = min(len(a), len(b))
rows = [(a[i], b[i]) for i in range(n)]
print('доля HF (дБ отн. полной энергии), 2-секундные окна, первые 60 с:')
for i, (x, y) in enumerate(rows[:20]):
    print('  %2d: тема %6.1f  микс %6.1f  разница %+5.1f' % (2 * i, x, y, y - x))
d = [y - x for x, y in rows]
print('медиана разницы %+.1f дБ, min %+.1f, max %+.1f' % (float(np.median(d)), min(d), max(d)))
