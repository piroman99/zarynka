# -*- coding: utf-8 -*-
"""Фикс: файлы озвучки были WAV с расширением .mp3. Транскод в настоящий mp3 (mono 96k)."""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
D = os.path.join(HERE, 'vn2', 'audio', 'vo')

tot_before = tot_after = 0
n = 0
for f in sorted(os.listdir(D)):
    p = os.path.join(D, f)
    if not os.path.isfile(p) or not f.endswith('.mp3'):
        continue
    with open(p, 'rb') as fh:
        head = fh.read(4)
    if head != b'RIFF':
        continue
    tmp = p + '.tmp.mp3'
    r = subprocess.run([FF, '-y', '-i', p, '-ar', '44100', '-ac', '1', '-b:a', '96k', tmp],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print('FAIL', f, r.stderr[-200:]); continue
    b = os.path.getsize(p); a = os.path.getsize(tmp)
    tot_before += b; tot_after += a
    os.replace(tmp, p)
    n += 1
print('транскодировано %d файлов: %.1f МБ -> %.1f МБ' % (n, tot_before / 1e6, tot_after / 1e6))
