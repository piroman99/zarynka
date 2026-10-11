# -*- coding: utf-8 -*-
"""Проверка черновика-аниматика пролога: ffprobe + нарезка контрольных кадров."""
import os, subprocess, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.abspath(os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg',
                                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2'))
MP4 = os.path.join(HERE, 'out', 'prolog_animatic_draft.mp4')
SHOT = os.path.join(HERE, 'assets', 'review', 'prolog_draft')

# 1) ffprobe
r = subprocess.run([FF, '-hide_banner', '-i', MP4], capture_output=True, text=True)
for ln in r.stderr.splitlines():
    if any(k in ln for k in ('Duration', 'Stream', 'fps')):
        print(ln.strip())

# 2) контрольные кадры
os.makedirs(SHOT, exist_ok=True)
ts = [2, 10, 24, 40, 52, 66, 80]
for t in ts:
    p = os.path.join(SHOT, 't%03d.png' % t)
    subprocess.run([FF, '-y', '-ss', str(t), '-i', MP4, '-frames:v', '1', p],
                   capture_output=True)
    print('frame', t, 's ->', os.path.relpath(p, HERE), os.path.getsize(p))

# 3) сводка
print('\nsize', os.path.getsize(MP4), 'bytes')
