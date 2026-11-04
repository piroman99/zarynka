# -*- coding: utf-8 -*-
"""Длительности озвучки страниц пролога через ffmpeg (метаданные в stderr)."""
import glob
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries',
                  'ffmpeg-linux-x86_64-v7.0.2')

for f in ['s3_00', 's4_00', 's5a_00', 's5a_01', 's5b_00']:
    p = os.path.join(HERE, 'vn2', 'audio', 'vo', f + '.mp3')
    r = subprocess.run([FF, '-hide_banner', '-i', p], capture_output=True, text=True)
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', r.stderr)
    dur = (int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))) if m else 0
    print('%-8s %7.2f с  %d B' % (f, dur, os.path.getsize(p)))
