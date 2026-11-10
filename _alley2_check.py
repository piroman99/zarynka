# -*- coding: utf-8 -*-
"""Проверка новых материалов «аллеи» (B+C): амбиент/тема/микс по полосам + картинки."""
import os
import subprocess

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
O = os.path.join(HERE, 'assets', 'audio', 'sketch')
SR = 22050
BANDS = [('sub20-80', 20, 80), ('low80-250', 80, 250), ('lowmid250-800', 250, 800),
         ('mid0.8-2k', 800, 2000), ('himid2-6k', 2000, 6000), ('air6-11k', 6000, 11000)]


def pcm(path):
    raw = subprocess.run([FF, '-hide_banner', '-v', 'error', '-i', path, '-f', 'f32le',
                          '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def rms_db(x):
    return 20 * np.log10(max(float(np.sqrt((x ** 2).mean())), 1e-12))


def bands(x):
    n = SR * 4
    acc = np.zeros(len(BANDS))
    tot = 0
    for i in range(0, len(x) - n, n):
        seg = x[i:i + n] * np.hanning(n)
        sp = np.abs(np.fft.rfft(seg)) ** 2
        f = np.fft.rfftfreq(n, 1 / SR)
        s = sp.sum()
        if s <= 0:
            continue
        for k, (_, a, b) in enumerate(BANDS):
            acc[k] += sp[(f >= a) & (f < b)].sum() / s
        tot += 1
    return acc / max(tot, 1)


files = ['alley_amb.mp3', 'alley2_amb.mp3', 'alley_bed.mp3', 'alley2_bed.mp3',
         'alley_mix.mp3', 'alley2_mix.mp3', 'alley2_mix_soft.mp3',
         'vn_reception_soft_0.mp3']
print('%-22s %8s %6s  %s' % ('файл', 'RMS', 'длина', '  '.join(b[0] for b in BANDS)))
for f in files:
    p = os.path.join(O, f)
    if not os.path.exists(p):
        print('%-22s нет' % f)
        continue
    x = pcm(p)
    b = bands(x)
    print('%-22s %6.1f dB %5.0fс  %s' % (f, rms_db(x), len(x) / SR,
                                         '  '.join('%11.1f' % (100 * v) for v in b)))

# шов петли амбиента: скачок на границе файла
a = pcm(os.path.join(O, 'alley2_amb.mp3'))
if len(a):
    jump = abs(float(a[-1] - a[0]))
    typical = float(np.abs(np.diff(a[:SR])).mean())
    print('\nпетля alley2_amb: скачок на стыке %.4f, типичный шаг %.4f -> %s'
          % (jump, typical, 'шва не слышно' if jump < 8 * typical + 1e-4 else 'ЩЕЛЧОК'))

print('\n--- картинки ---')
for rel in ['assets/gen/bench2_0.png', 'assets/gen/sit2_smile2_0.png',
            'assets/gen/sit_smile_0.png', 'assets/gen/prop_bench.png',
            'assets/sprites/prop_bench.png', 'assets/sprites/poet_seat_smile.png']:
    p = os.path.join(HERE, rel)
    if not os.path.exists(p):
        print('%-42s НЕТ' % rel)
        continue
    im = Image.open(p)
    extra = ''
    if im.mode == 'RGBA':
        al = np.asarray(im.split()[-1])
        ys, xs = np.nonzero(al > 20)
        if len(xs):
            extra = (' альфа: x %d..%d y %d..%d (%.0f%% кадра по ширине, %.0f%% по высоте)'
                     % (xs.min(), xs.max(), ys.min(), ys.max(),
                        100.0 * (xs.max() - xs.min()) / im.width,
                        100.0 * (ys.max() - ys.min()) / im.height))
    print('%-42s %s %s %d Б%s' % (rel, im.mode, '%dx%d' % im.size,
                                  os.path.getsize(p), extra))
