# -*- coding: utf-8 -*-
"""Спектр по полосам: что именно «приземляет» амбиент аллеи и сколько его в миксе.

Полосы: sub 20-80, низ 80-250, низ-сред 250-800, сред 0.8-2k, верх-сред 2-6k,
воздух 6-12k. Печатаем долю энергии каждой полосы (%) для amb / bed / mix.
"""
import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
O = os.path.join(ROOT, 'assets', 'audio', 'sketch')
SR = 22050

BANDS = [('sub 20-80', 20, 80), ('низ 80-250', 80, 250), ('низ-ср 250-800', 250, 800),
         ('сред 0.8-2k', 800, 2000), ('верх-ср 2-6k', 2000, 6000),
         ('воздух 6-11k', 6000, 11000)]


def pcm(path):
    raw = subprocess.run([FF, '-hide_banner', '-v', 'error', '-i', path, '-f', 'f32le',
                          '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def bands(x):
    # среднее по кускам по 4 с — устойчивее к случайным пикам
    n = SR * 4
    acc = np.zeros(len(BANDS))
    total = 0.0
    for i in range(0, len(x) - n, n):
        seg = x[i:i + n] * np.hanning(n)
        sp = np.abs(np.fft.rfft(seg)) ** 2
        f = np.fft.rfftfreq(n, 1 / SR)
        s = sp.sum()
        if s <= 0:
            continue
        for k, (_, a, b) in enumerate(BANDS):
            acc[k] += sp[(f >= a) & (f < b)].sum() / s
        total += 1
    return acc / max(total, 1)


def rms_db(x):
    return 20 * np.log10(max(float(np.sqrt((x ** 2).mean())), 1e-12))


files = ['alley_amb.mp3', 'alley_bed.mp3', 'alley_mix.mp3', 'alley_bed_mix_0.mp3']
print('%-20s %8s  %s' % ('файл', 'RMS', '  '.join('%s' % b[0] for b in BANDS)))
for f in files:
    p = os.path.join(O, f)
    if not os.path.exists(p):
        print('%-20s нет' % f)
        continue
    x = pcm(p)
    b = bands(x)
    print('%-20s %6.1f dB  %s' % (f, rms_db(x),
                                  '  '.join('%9.1f%%' % (100 * v) for v in b)))

# сколько амбиента реально в миксе: вычитаем тему из микса (обе сведены по времени)
amb = pcm(os.path.join(O, 'alley_amb.mp3'))
bed = pcm(os.path.join(O, 'alley_bed.mp3'))
mix = pcm(os.path.join(O, 'alley_mix.mp3'))
n = min(len(amb), len(bed), len(mix))
print('\nдлины: amb %.0f c, bed %.0f c, mix %.0f c' % (len(amb) / SR, len(bed) / SR, len(mix) / SR))

# корреляция микса с темой и с амбиентом — кто в миксе громче «звучит»
def corr(a, b):
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    a = a - a.mean()
    b = b - b.mean()
    d = np.sqrt((a ** 2).sum() * (b ** 2).sum())
    return float((a * b).sum() / d) if d > 0 else 0.0

print('корреляция mix~bed  %.3f' % corr(mix, bed))
print('корреляция mix~amb  %.3f' % corr(mix, amb))
