# -*- coding: utf-8 -*-
"""Проверка интро: длительность/потоки + постер-кадры."""
import os, subprocess
FF = "/home/ivan/.nanobot/workspace/.probe/.lib/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
HERE = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(HERE, "out", "intro_animatic.mp4")

r = subprocess.run([FF, "-i", V], capture_output=True, text=True)
for line in r.stderr.splitlines():
    if any(k in line for k in ("Duration", "Stream", "Video:", "Audio:")):
        print(line.strip())

for t in ("00:00:02", "00:00:10", "00:00:18"):
    p = os.path.join(HERE, ".tmp_intro", f"post_{t.replace(':','')}.png")
    subprocess.run([FF, "-y", "-ss", t, "-i", V, "-frames:v", "1", p], capture_output=True, text=True)
    print("poster:", os.path.relpath(p, HERE), os.path.exists(p))
