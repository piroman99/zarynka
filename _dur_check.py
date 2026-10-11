# -*- coding: utf-8 -*-
"""Проверка: длительности VO v2 и музыкальных скетчей."""
import wave, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.abspath(os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg',
                                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2'))


def wdur(p):
    with wave.open(p, 'rb') as w:
        return w.getnframes() / float(w.getframerate())


tot = 0
for n in ['s1', 's2', 's3', 's4', 's5', 's6']:
    d = wdur(os.path.join(HERE, 'assets', 'audio', 'vo_prolog2', n + '_0.wav'))
    print(n, round(d, 2))
    tot += d
print('VO total %.2f s | +P0(6s) = %.2f s (%.2f мин)' % (tot, tot + 6, (tot + 6) / 60))
print()
for f in ['assets/audio/sketch/prolog_bed_soft_0.mp3',
          'assets/audio/sketch/prolog_bed_ambient_0.mp3',
          'assets/audio/sketch/vn_reception_soft_0.mp3',
          'assets/audio/sketch/vn_reception_lullaby_0.mp3',
          'assets/audio/sketch/vn_space_0.mp3']:
    r = subprocess.run([FF, '-hide_banner', '-i', f], capture_output=True, text=True)
    for ln in r.stderr.splitlines():
        if 'Duration' in ln:
            print(f, '->', ln.strip())
