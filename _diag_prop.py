# -*- coding: utf-8 -*-
"""Диагностика пропорций: круг в исходнике (портрет) -> кадр после kb() должен остаться кругом.
Если стал эллипсом -> zoompan растягивает (aspect не сохраняется)."""
import os, subprocess
from PIL import Image, ImageDraw
import numpy as np

FF = "/home/ivan/.nanobot/workspace/.probe/.lib/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
HERE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(HERE, ".tmp_diag")
os.makedirs(TMP, exist_ok=True)

W, H = 1920, 1080
src = os.path.join(TMP, "circle_3x4.png")
im = Image.new("RGB", (900, 1200), (20, 20, 30))
d = ImageDraw.Draw(im)
d.ellipse([250, 450, 650, 850], outline=(255, 255, 255), width=8)  # круг 400x400
im.save(src)

def kb(src, dst, secs=1.0, fps=25):
    z = "min(1+0.0009*on,1.18)"
    vf = (f"scale={W*2}:-2,zoompan=z='{z}':d=1:"
          f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={fps},"
          f"setsar=1,format=yuv420p")
    subprocess.run([FF, "-y", "-loop", "1", "-t", str(secs), "-i", src, "-vf", vf,
                    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23", dst],
                   capture_output=True, text=True)
    return dst

vid = kb(src, os.path.join(TMP, "circle.mp4"))
png = os.path.join(TMP, "frame.png")
subprocess.run([FF, "-y", "-i", vid, "-frames:v", "1", png], capture_output=True, text=True)
a = np.array(Image.open(png).convert("L"))
ys, xs = np.where(a > 120)
if len(xs) == 0:
    print("no bright pixels found")
else:
    w = xs.max() - xs.min() + 1
    h = ys.max() - ys.min() + 1
    print(f"frame={a.shape[1]}x{a.shape[0]}  circle bbox = {w}x{h}  ratio w/h = {w/h:.3f}")
    print("Круг = ок" if abs(w/h - 1) < 0.06 else "ЭЛЛИПС -> пропорции искажены!")

# stream of existing animatic
r = subprocess.run([FF, "-i", os.path.join(HERE, "out", "intro_animatic.mp4")],
                   capture_output=True, text=True)
for line in r.stderr.splitlines():
    if "Video:" in line or "Audio:" in line:
        print("ANIMATIC:", line.strip())
