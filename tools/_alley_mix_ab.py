# -*- coding: utf-8 -*-
"""A/B-перебалансировка сцены «аллея» (0 ₽, без генерации).

ЗАМЕР, почему Ивану «амбиент громкий, а музыка не та»:
  alley_amb.mp3  RMS -30.1 dB, длина всего 22 с (петля), 89 % энергии выше 2 кГц
                 (2-6 кГц 61.5 %, 6-11 кГц 28.4 %) — это тонкий шипящий шум, а не улица:
                 ни ветра (80-300 Гц), ни птиц, ни отражений;
  alley_bed.mp3  RMS -20.8 dB, наоборот глухая и басовая: 9.7 % ниже 80 Гц,
                 36.8 % 80-250, 45.8 % 250-800, а выше 2 кГц всего 1.1 %.
  alley_mix.mp3  = эти двое; вклад амбиента по RMS +0.4 дБ (corr 0.003), но его шипение
                 сидит в той полосе, где у музыки пусто -> слышно «громко» именно его.

Варианты (обе громкости выровнены по теме приёмной -20.8 dBFS, как было):
  a1 — амбиент -6 дБ и срез 350 Гц..10 кГц (шипение убрано, музыка вперёд);
  a2 — амбиент -12 дБ + у темы убрать 200 Гц (-2 дБ) и добавить воздух 3 кГц (+1.5 дБ).

Выход: assets/audio/sketch/ab_alley_a1.mp3, ab_alley_a2.mp3
Запуск: python3 _alley_mix_ab.py
"""
import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
O = os.path.join(ROOT, 'assets', 'audio', 'sketch')
SR = 44100
REF_RMS = -20.8          # громкость темы приёмной (vn_reception_soft_0.mp3)

BED = os.path.join(O, 'alley_bed_0.mp4')
AMB = os.path.join(O, 'alley_amb_0.mp3')


def pcm(path, ac=1):
    raw = subprocess.run([FF, '-hide_banner', '-v', 'error', '-i', path, '-f', 'f32le',
                          '-ac', str(ac), '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def rms_db(x):
    return 20 * np.log10(max(float(np.sqrt((x ** 2).mean())), 1e-12))


def bands(x):
    B = [('sub', 20, 80), ('low', 80, 250), ('lowmid', 250, 800), ('mid', 800, 2000),
         ('himid', 2000, 6000), ('air', 6000, 11000)]
    n = SR * 4
    acc = np.zeros(len(B))
    tot = 0
    for i in range(0, len(x) - n, n):
        seg = x[i:i + n] * np.hanning(n)
        sp = np.abs(np.fft.rfft(seg)) ** 2
        f = np.fft.rfftfreq(n, 1 / SR)
        s = sp.sum()
        if s <= 0:
            continue
        for k, (_, a, b) in enumerate(B):
            acc[k] += sp[(f >= a) & (f < b)].sum() / s
        tot += 1
    return acc / max(tot, 1)


VARIANTS = [
    ('a1', -6.0, 350, 10000, ''),
    ('a2', -12.0, 400, 9000,
     'equalizer=f=200:width_type=o:width=1.2:g=-2,equalizer=f=3000:width_type=o:width=1.5:g=1.5,'),
]

rms_amb = rms_db(pcm(AMB))
rms_bed = rms_db(pcm(BED))
print('bed RMS %.1f dBFS | amb RMS %.1f dBFS | разница %.1f дБ'
      % (rms_bed, rms_amb, rms_bed - rms_amb))

for tag, delta, hp, lp, bedeq in VARIANTS:
    # целевой уровень амбиента = текущий (-30.1) + delta
    gain = (-30.1 + delta) - rms_amb
    fc = ("[1:a]aloop=loop=-1:size=2e9,volume=%.2fdB,highpass=f=%d,lowpass=f=%d,"
          "alimiter=limit=0.30:level=disabled,afade=t=in:st=0:d=2[amb];"
          "[0:a]%svolume=0dB[bed];"
          "[bed][amb]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
          "alimiter=limit=0.95:level=disabled[m]") % (gain, hp, lp, bedeq)
    tmp = os.path.join(O, '_ab_%s.wav' % tag)
    r = subprocess.run([FF, '-y', '-v', 'error', '-i', BED, '-i', AMB, '-filter_complex', fc,
                        '-map', '[m]', '-c:a', 'pcm_s16le', tmp], capture_output=True, text=True)
    if r.returncode:
        print('%s: ffmpeg rc=%d %s' % (tag, r.returncode, (r.stderr or '')[-300:]))
        continue
    x = pcm(tmp)
    trim = REF_RMS - rms_db(x)
    dst = os.path.join(O, 'ab_alley_%s.mp3' % tag)
    r = subprocess.run([FF, '-y', '-v', 'error', '-i', tmp,
                        '-af', 'volume=%.2fdB' % trim,
                        '-c:a', 'libmp3lame', '-b:a', '112k', '-ac', '2', dst],
                       capture_output=True, text=True)
    os.remove(tmp)
    y = pcm(dst)
    b = bands(y)
    print('%s: амбиент %+.1f дБ, HP %d/LP %d, подстройка %+.1f дБ -> RMS %.1f dBFS  '
          '| sub %.0f low %.0f lowmid %.0f mid %.0f himid %.0f air %.0f (%%)'
          % (tag, delta, hp, lp, trim, rms_db(y), *[100 * v for v in b]))
    print('    файл:', os.path.basename(dst), '%d Б' % os.path.getsize(dst))
