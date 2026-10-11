# -*- coding: utf-8 -*-
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.abspath(os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg',
                                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2'))
MP4 = os.path.join(HERE, 'out', 'prolog_animatic_draft.mp4')
D = os.path.join(HERE, 'assets', 'review', 'prolog_draft')
os.makedirs(D, exist_ok=True)
for t in [35.0, 37.0, 43.5, 66.0, 69.0, 71.5, 86.5]:
    p = os.path.join(D, 'v3_t%04.1f.png' % t)
    subprocess.run([FF, '-y', '-ss', str(t), '-i', MP4, '-frames:v', '1', p], capture_output=True)
    print(t, os.path.getsize(p))
