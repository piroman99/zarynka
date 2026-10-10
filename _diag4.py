# -*- coding: utf-8 -*-
import os, subprocess, glob
FF = "/home/ivan/.nanobot/workspace/.probe/.lib/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
for p in sorted(glob.glob("assets/gen/vid/*.mp4")):
    r = subprocess.run([FF, "-hide_banner", "-i", p], capture_output=True, text=True)
    info = [l.strip() for l in r.stderr.splitlines() if "Duration" in l or "Stream #" in l]
    print(p, round(os.path.getsize(p)/1e6, 2), "MB")
    for l in info:
        print("   ", l)
