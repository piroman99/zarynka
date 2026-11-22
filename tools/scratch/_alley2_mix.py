# -*- coding: utf-8 -*-
"""Сборка НОВОГО звука сцены «аллея» (B+C, решение Ивана 2026-11-10).

Материалы:
  alley2_bed_0.mp4 — тема (lyria-3-5, 154 с, RMS -19.8 dBFS)
  alley2_amb_0.mp3 — улица (elevenlabs-sfx, 22 с петля, но ОЧЕНЬ тихая: пик 0.02,
                     RMS -66 dBFS; модель всегда отдаёт такой уровень — поднимаем сами)

Обработка:
  • тема: HP 55 Гц, -2.5 дБ на 350 Гц (убираем «коробку» 250-800 Гц, её там 70 %),
    +2 дБ полкой на 4 кГц (воздух; выше 6 кГц у lyria пусто, см. замер);
  • улица: петля 22 с -> 44 с приёмом «вперёд + назад» (шов не слышен),
    HP 200 / LP 11k, RMS -35 dBFS (15 дБ под темой);
  • микс выравнивается по теме приёмной (-20.8 dBFS), чтобы сцены не щёлкали уровнем.

Выход: alley2_mix.mp3 (рабочий), alley2_mix_soft.mp3 (улица -42), alley2_bed.mp3,
alley2_amb.mp3 (соло, для прослушивания).
"""
import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
O = os.path.join(ROOT, 'assets', 'audio', 'sketch')
SR = 44100
REF_RMS = -20.8

BED = os.path.join(O, 'alley2_bed_0.mp4')
AMB = os.path.join(O, 'alley2_amb_0.mp3')

BANDS = [('sub', 20, 80), ('low', 80, 250), ('lowmid', 250, 800), ('mid', 800, 2000),
         ('himid', 2000, 6000), ('air', 6000, 11000)]


def pcm(path, ac=1, sr=SR):
    raw = subprocess.run([FF, '-hide_banner', '-v', 'error', '-i', path, '-f', 'f32le',
                          '-ac', str(ac), '-ar', str(sr), '-'], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def rms_db(x):
    return 20 * np.log10(max(float(np.sqrt((x ** 2).mean())), 1e-12))


def bands(x):
    n = SR * 4
    acc = np.zeros(len(BANDS))
    tot = 0
    for i in range(0, max(len(x) - n, 1), n):
        seg = x[i:i + n]
        if len(seg) < n:
            break
        seg = seg * np.hanning(n)
        sp = np.abs(np.fft.rfft(seg)) ** 2
        f = np.fft.rfftfreq(n, 1 / SR)
        s = sp.sum()
        if s <= 0:
            continue
        for k, (_, a, b) in enumerate(BANDS):
            acc[k] += sp[(f >= a) & (f < b)].sum() / s
        tot += 1
    return acc / max(tot, 1)


BED_EQ = ('highpass=f=55,equalizer=f=350:width_type=o:width=1.6:g=-2.5,'
          'equalizer=f=4000:width_type=o:width=1.2:g=2.0,')

rms_amb_raw = rms_db(pcm(AMB))
print('улица сырая: RMS %.1f dBFS (поднимаем на %.1f дБ)' % (rms_amb_raw, -35.0 - rms_amb_raw))

jobs = [('alley2_mix', -35.0), ('alley2_mix_soft', -42.0)]
for tag, amb_target in jobs:
    gain = amb_target - rms_amb_raw
    fc = ("[1:a]volume=%.2fdB,highpass=f=200,lowpass=f=11000,"
          "aloop=loop=-1:size=2e9,alimiter=limit=0.5:level=disabled,"
          "afade=t=in:st=0:d=1.5[amb];"
          "[0:a]%salimiter=limit=0.95:level=disabled[bed];"
          "[bed][amb]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
          "alimiter=limit=0.95:level=disabled[m]") % (gain, BED_EQ)
    tmp = os.path.join(O, '_%s.wav' % tag)
    r = subprocess.run([FF, '-y', '-v', 'error', '-i', BED, '-i', AMB, '-filter_complex', fc,
                        '-map', '[m]', '-c:a', 'pcm_s16le', tmp], capture_output=True, text=True)
    if r.returncode:
        print('%s: ffmpeg rc=%d %s' % (tag, r.returncode, (r.stderr or '')[-400:]))
        continue
    x = pcm(tmp)
    trim = REF_RMS - rms_db(x)
    dst = os.path.join(O, tag + '.mp3')
    r = subprocess.run([FF, '-y', '-v', 'error', '-i', tmp, '-af', 'volume=%.2fdB' % trim,
                        '-c:a', 'libmp3lame', '-b:a', '128k', '-ac', '2', dst],
                       capture_output=True, text=True)
    os.remove(tmp)
    y = pcm(dst)
    b = bands(y)
    print('%-18s улица %.0f dBFS, подстройка %+.1f дБ -> RMS %.1f dBFS, %.0f с'
          % (tag, amb_target, trim, rms_db(y), len(y) / SR))
    print('   полосы: ' + '  '.join('%s %.0f%%' % (BANDS[i][0], 100 * v)
                                    for i, v in enumerate(b)))
    print('   файл: %s (%d Б)' % (os.path.basename(dst), os.path.getsize(dst)))

# соло-версии для прослушивания: тема с EQ и улица в рабочем уровне
for tag, src, filt in (('alley2_bed', BED, BED_EQ + 'alimiter=limit=0.95'),
                       ('alley2_amb', AMB,
                        'volume=%.2fdB,highpass=f=200,lowpass=f=11000,alimiter=limit=0.9'
                        % (-35.0 - rms_amb_raw))):
    dst = os.path.join(O, tag + '.mp3')
    r = subprocess.run([FF, '-y', '-v', 'error', '-i', src, '-af', filt,
                        '-c:a', 'libmp3lame', '-b:a', '128k', '-ac', '2', dst],
                       capture_output=True, text=True)
    y = pcm(dst)
    print('%-18s RMS %.1f dBFS, %.0f с' % (tag, rms_db(y), len(y) / SR))
