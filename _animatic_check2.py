# -*- coding: utf-8 -*-
"""Контроль: кадры аниматика + громкость двух дорожек (VO / подстрочник)."""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.abspath(os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg',
                                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2'))
MP4 = os.path.join(HERE, 'out', 'prolog_animatic_draft.mp4')
SUB = os.path.join(HERE, 'out', 'prolog_animatic_subs.mp4')
SHOT = os.path.join(HERE, 'assets', 'review', 'prolog_draft')
os.makedirs(SHOT, exist_ok=True)
for t in [3, 12, 25, 40, 53, 65, 80]:
    p = os.path.join(SHOT, 'v2_t%03d.png' % t)
    subprocess.run([FF, '-y', '-ss', str(t), '-i', MP4, '-frames:v', '1', p], capture_output=True)
    print('frame', t, os.path.getsize(p))
for tag, f in (('VO ', MP4), ('SUB', SUB)):
    r = subprocess.run([FF, '-hide_banner', '-i', f, '-af', 'volumedetect', '-f', 'null', '-'],
                       capture_output=True, text=True)
    for ln in r.stderr.splitlines():
        if 'mean_volume' in ln or 'max_volume' in ln or 'Duration' in ln:
            print(tag, ln.strip())
