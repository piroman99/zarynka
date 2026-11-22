# -*- coding: utf-8 -*-
"""Глубокий разбор новых материалов: (1) почему amb такой тихий и не шипит ли он,
(2) есть ли у темы верх выше 6 кГц (в 22 кГц-анализе его не было).

Для амбиента: RMS по окнам 0.5 с (есть ли «порывы ветра» = динамика), спектральная
плоскостность (шум/тон) в громких и тихих окнах, доля энергии выше 8 кГц.
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


def pcm(path, sr=SR):
    raw = subprocess.run([FF, '-hide_banner', '-v', 'error', '-i', path, '-f', 'f32le',
                          '-ac', '1', '-ar', str(sr), '-'], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def rms_db(x):
    return 20 * np.log10(max(float(np.sqrt((x ** 2).mean())), 1e-12))


def info(path, label):
    x = pcm(path)
    print('\n=== %s ===' % label)
    print('длина %.1f с, RMS %.1f dBFS, пик %.3f' % (len(x) / SR, rms_db(x), np.abs(x).max()))
    # окна 0.5 с
    n = SR // 2
    wins = [x[i:i + n] for i in range(0, len(x) - n, n)]
    wr = np.array([rms_db(w) for w in wins])
    print('окна 0.5 с: мин %.1f, медиана %.1f, макс %.1f дБ (разброс %.1f дБ)'
          % (wr.min(), np.median(wr), wr.max(), wr.max() - wr.min()))
    # спектральная плоскостность в громком и тихом окне
    def flat(w):
        sp = np.abs(np.fft.rfft(w * np.hanning(len(w)))) ** 2 + 1e-18
        return float(np.exp(np.log(sp).mean()) / sp.mean())
    idx = np.argsort(wr)
    quiet = flat(wins[idx[1]])
    loud = flat(wins[idx[-2]])
    print('спектр. плоскостность: тихое окно %.3f, громкое %.3f (1.0 = чистый шум)' % (quiet, loud))
    # полосы до 16 кГц
    seg = x[:SR * 8] * np.hanning(SR * 8)
    sp = np.abs(np.fft.rfft(seg)) ** 2
    f = np.fft.rfftfreq(len(seg), 1 / SR)
    for a, b in ((6000, 8000), (8000, 11000), (11000, 16000)):
        print('  %5d-%5d Гц: %.2f%%' % (a, b, 100.0 * sp[(f >= a) & (f < b)].sum() / sp.sum()))


info(os.path.join(O, 'alley2_amb_0.mp3'), 'amb НОВЫЙ (alley2_amb_0.mp3)')
info(os.path.join(O, 'alley2_bed_0.mp4'), 'bed НОВЫЙ (alley2_bed_0.mp4)')
info(os.path.join(O, 'alley_bed.mp3'), 'bed старый')
