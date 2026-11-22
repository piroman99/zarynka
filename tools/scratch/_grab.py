# -*- coding: utf-8 -*-
"""Вытащить кадры из собранного интро, чтобы глазами проверить пропорции."""
import os, subprocess
FF = "/home/ivan/.nanobot/workspace/.probe/.lib/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
os.makedirs(".tmp_diag", exist_ok=True)
for t in (2.0, 5.0, 9.0, 13.0, 17.0, 21.0):
    out = f".tmp_diag/f_{int(t):02d}.png"
    r = subprocess.run([FF, "-y", "-ss", str(t), "-i", "out/intro_animatic.mp4",
                        "-frames:v", "1", "-vf", "scale=960:-1", out],
                       capture_output=True, text=True)
    print(out, r.returncode, os.path.exists(out))
