# -*- coding: utf-8 -*-
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.abspath(os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg',
                                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2'))
for rel in sys.argv[1:]:
    p = os.path.join(HERE, rel)
    info = subprocess.run([FF, '-hide_banner', '-i', p], capture_output=True, text=True).stderr
    print('==', rel, os.path.getsize(p), 'B')
    for l in info.splitlines():
        if any(k in l for k in ('Duration', 'Stream', 'Audio', 'Video')):
            print('   ', l.strip())
