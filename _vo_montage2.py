# -*- coding: utf-8 -*-
"""Чистая дорожка голоса пролога v2 (без музыки) — для прослушки интонации.
Склейка замедленных s1..s6 -> assets/audio/vo_prolog2/vo_prolog2_all.mp3
"""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.abspath(os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg',
                                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2'))
SRC = os.path.join(HERE, 'assets', 'audio', 'vo_prolog2')
SLOW = os.path.join(HERE, '.tmp_animatic', 'vo_slow')
OUT = os.path.join(SRC, 'vo_prolog2_all.mp3')
names = ['s1', 's2', 's3', 's4', 's5', 's6']
inputs = []
for n in names:
    p = os.path.join(SLOW, n + '.wav')
    if not os.path.exists(p):
        p = os.path.join(SRC, n + '_0.wav')
    inputs += ['-i', p]
fc = ''.join('[%d:a]' % i for i in range(len(names))) + 'concat=n=%d:v=0:a=1[out]' % len(names)
cmd = [FF, '-y'] + inputs + ['-filter_complex', fc, '-map', '[out]', '-ar', '44100', '-b:a', '160k', OUT]
r = subprocess.run(cmd, capture_output=True, text=True)
print('rc', r.returncode, os.path.getsize(OUT) if os.path.exists(OUT) else 0)
