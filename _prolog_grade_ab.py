# -*- coding: utf-8 -*-
"""A/B-клип грейда: слева «как есть», справа «тёплый архив» (реком.).
Один быстрый проход ffmpeg по готовому аниматику (без перерендера).
Выход: out/prolog_grade_ab.mp4 (3840x1080).
"""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.abspath(os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg',
                                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2'))
SRC = os.path.join(HERE, 'out', 'prolog_animatic_draft.mp4')
OUT = os.path.join(HERE, 'out', 'prolog_grade_ab.mp4')
F = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'


# в этом сборке ffmpeg нет drawtext -> только hstack (лев./прав. подписаны в чате)
fc = ("[0:v]split=2[a][b];"
      "[b]hue=s=0.62,colorbalance=rs=0.06:rm=0.02:bs=-0.07:bm=-0.02,"
      "eq=contrast=1.07:brightness=0.01[bv];"
      "[a][bv]hstack=inputs=2[v]")
cmd = [FF, '-y', '-i', SRC, '-filter_complex', fc, '-map', '[v]', '-map', '0:a',
       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22', '-pix_fmt', 'yuv420p',
       '-c:a', 'copy', OUT]
r = subprocess.run(cmd, capture_output=True, text=True)
print('rc', r.returncode)
if r.returncode:
    print(r.stderr[-1500:])
else:
    print('saved', os.path.relpath(OUT, HERE), os.path.getsize(OUT), 'bytes')
