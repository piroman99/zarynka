# -*- coding: utf-8 -*-
"""Анализ НОВЫХ материалов «аллеи» (B+C) и сборка финального микса.

Правило баланса, выведенное из замера старых файлов: амбиент не должен спорить с темой
в той же полосе. Тема новая — сначала смотрим её полосы, потом решаем срез амбиента.

Сборка:
  • петля 22 с разворачивается в 44 с приёмом «вперёд + назад» (шов не слышен);
  • амбиент идёт под темой на ~13 дБ по RMS, HP 200 / LP 11k;
  • громкость микса выравнивается по теме приёмной (-20.8 dBFS), как у остальных сцен.
"""
import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
O = os.path.join(ROOT, 'assets', 'audio', 'sketch')
SR = 22050

B = [('sub 20-80', 20, 80), ('низ 80-250', 80, 250), ('низ-ср 250-800', 250, 800),
     ('сред 0.8-2k', 800, 2000), ('верх-ср 2-6k', 2000, 6000),
     ('воздух 6-11k', 6000, 11000)]


def pcm(path, ac=1, sr=SR):
    raw = subprocess.run([FF, '-hide_banner', '-v', 'error', '-i', path, '-f', 'f32le',
                          '-ac', str(ac), '-ar', str(sr), '-'], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def rms_db(x):
    return 20 * np.log10(max(float(np.sqrt((x ** 2).mean())), 1e-12))


def bands(x, sr=SR):
    n = sr * 4
    acc = np.zeros(len(B))
    tot = 0
    for i in range(0, max(len(x) - n, 1), n):
        seg = x[i:i + n]
        if len(seg) < n:
            break
        seg = seg * np.hanning(n)
        sp = np.abs(np.fft.rfft(seg)) ** 2
        f = np.fft.rfftfreq(n, 1 / sr)
        s = sp.sum()
        if s <= 0:
            continue
        for k, (_, a, b) in enumerate(B):
            acc[k] += sp[(f >= a) & (f < b)].sum() / s
        tot += 1
    return acc / max(tot, 1)


def report(label, path):
    x = pcm(path)
    b = bands(x)
    print('%-22s RMS %6.1f dBFS  пик %4.2f  %5.1f с  | %s'
          % (label, rms_db(x), float(np.abs(x).max()), len(x) / SR,
             ' '.join('%.0f%%' % (100 * v) for v in b)))
    return b


print('полосы:', ' | '.join(b[0] for b in B))
for f, lab in (('alley2_amb_0.mp3', 'amb НОВЫЙ'), ('alley2_bed_0.mp4', 'bed НОВЫЙ'),
               ('alley_amb.mp3', 'amb старый'), ('alley_bed.mp3', 'bed старый')):
    p = os.path.join(O, f)
    if os.path.exists(p):
        report(lab, p)
