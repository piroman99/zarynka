# -*- coding: utf-8 -*-
"""Проверка v2: круг в портретном источнике через НОВЫЙ конвейер (contain+blur -> zoompan)
должен остаться кругом. Плюс вытащить кадры из нового аниматика."""
import os, subprocess
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(HERE, ".tmp_intro")
FF = "/home/ivan/.nanobot/workspace/.probe/.lib/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
W, H, FPS = 1920, 1080, 25


def _cover(im, w, h):
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def _contain(im, w, h):
    r = min(w / im.width, h / im.height)
    return im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)


def fit16(src):
    im = Image.open(src).convert("RGB")
    bg = _cover(im, W, H).filter(ImageFilter.GaussianBlur(46))
    bg = Image.eval(bg, lambda v: int(v * 0.55))
    fg = _contain(im, W, H)
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    p = os.path.join(TMP, "diag_fit_%s.png" % os.path.basename(src).rsplit(".", 1)[0])
    bg.save(p)
    return p


def kb(src, dst, secs, mode="in"):
    frames = max(2, int(secs * FPS))
    if mode == "in":
        z, x, y = "min(1+0.0013*on,1.16)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    else:
        z, x, y = "max(1.16-0.0013*on,1.0)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    vf = (f"scale={W*2}:{H*2},zoompan=z='{z}':d=1:x='{x}':y='{y}':s={W}x{H}:fps={FPS},"
          f"setsar=1,format=yuv420p")
    subprocess.run([FF, "-y", "-loop", "1", "-t", f"{secs:.3f}", "-i", src, "-vf", vf,
                    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", dst],
                   capture_output=True, text=True)
    return dst


src = os.path.join(TMP, "circle2_3x4.png")
im = Image.new("RGB", (900, 1200), (20, 20, 30))
ImageDraw.Draw(im).ellipse([250, 450, 650, 850], outline=(255, 255, 255), width=8)
im.save(src)
ready = fit16(src)
vid = kb(ready, os.path.join(TMP, "circle2.mp4"), 1.0, "in")
png = os.path.join(TMP, "circle2_frame.png")
subprocess.run([FF, "-y", "-i", vid, "-frames:v", "1", png], capture_output=True, text=True)
a = np.array(Image.open(png).convert("L"))
ys, xs = np.where(a > 140)
w = int(xs.max() - xs.min() + 1)
h = int(ys.max() - ys.min() + 1)
print(f"[v2] circle bbox = {w}x{h}  ratio w/h = {w/h:.3f}  ->  " +
      ("КРУГ (ок)" if abs(w / h - 1) < 0.06 else "ЭЛЛИПС (плохо)"))

final = os.path.join(HERE, "out", "intro_animatic.mp4")
for t in (1, 5, 9, 13, 17, 21, 25):
    out = os.path.join(TMP, f"post2_{t:02d}.png")
    subprocess.run([FF, "-y", "-ss", str(t), "-i", final, "-frames:v", "1", out],
                   capture_output=True, text=True)
    print("frame", t, os.path.exists(out))
