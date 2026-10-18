# -*- coding: utf-8 -*-
"""Оценка основного тона (F0) по файлам озвучки: мужской ~85-160 Гц, женский ~170-260.
Нужна, чтобы проверить, что Катя реально озвучена Charlotte, а не мужским голосом."""
import os, json, wave, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'vn2', 'audio', 'vo')
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries',
                  'ffmpeg-linux-x86_64-v7.0.2')
SR = 16000


def f0(path):
    tmp = path + '.f0.wav'
    subprocess.run([FF, '-y', '-i', path, '-ac', '1', '-ar', str(SR), tmp],
                   capture_output=True, text=True)
    w = wave.open(tmp)
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    w.close()
    os.remove(tmp)
    n = int(0.04 * SR)
    hop = int(0.02 * SR)
    lo, hi = int(SR / 300), int(SR / 70)
    est = []
    for i in range(0, max(0, len(a) - n), hop):
        fr = a[i:i + n]
        if np.sqrt((fr ** 2).mean()) < 0.02:
            continue
        fr = fr - fr.mean()
        c = np.correlate(fr, fr, 'full')[n - 1:]
        c /= (c[0] + 1e-9)
        seg = c[lo:hi]
        if not len(seg):
            continue
        k = int(np.argmax(seg)) + lo
        if c[k] > 0.32:
            est.append(SR / k)
    if not est:
        return None, 0
    return float(np.median(est)), len(est)


man = json.load(open(os.path.join(OUT, '_voices.json'), encoding='utf-8'))
rows = []
for name in sorted(man):
    p = os.path.join(OUT, os.path.basename(name))
    if not os.path.exists(p):
        continue
    m, cnt = f0(p)
    rows.append((os.path.basename(name), man[name]['voice'], m, cnt))

for nm, v, m, c in rows:
    print('%-12s %-10s F0=%s (%d кадров)' % (nm, v, '%.0f Гц' % m if m else '?', c))
