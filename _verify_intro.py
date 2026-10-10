# -*- coding: utf-8 -*-
"""Проверка v2 интро-аниматика: поток + кадры по секундам + контрольный лист."""
import os, subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FF = "/home/ivan/.nanobot/workspace/.probe/.lib/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
TMP = os.path.join(HERE, ".tmp_intro")
OUT = os.path.join(HERE, "assets", "review")
final = os.path.join(HERE, "out", "intro_animatic.mp4")

r = subprocess.run([FF, "-i", final], capture_output=True, text=True)
for line in r.stderr.splitlines():
    if "Duration" in line or "Video:" in line or "Audio:" in line:
        print("STREAM:", line.strip())

def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

times = [2, 5, 9, 13, 17, 21, 26]
cells = []
for t in times:
    out = os.path.join(TMP, f"v_{t:02d}.png")
    subprocess.run([FF, "-y", "-ss", str(t), "-i", final, "-frames:v", "1", out],
                   capture_output=True, text=True)
    if os.path.exists(out):
        cells.append((t, out))

CW, CH, LBL, PAD = 620, 349, 30, 14
cols = 2
rows = (len(cells) + cols - 1) // cols
W = cols * CW + (cols + 1) * PAD
H = rows * (CH + LBL) + (rows + 1) * PAD
sheet = Image.new("RGB", (W, H), (24, 26, 32))
d = ImageDraw.Draw(sheet)
f = font(20)
for i, (t, p) in enumerate(cells):
    rr, cc = divmod(i, cols)
    x = PAD + cc * (CW + PAD)
    y = PAD + rr * (CH + LBL + PAD)
    d.text((x, y), f"t = {t}s", fill=(235, 232, 226), font=f)
    im = Image.open(p).convert("RGB").resize((CW, CH), Image.LANCZOS)
    sheet.paste(im, (x, y + LBL))
out = os.path.join(OUT, "review_15_intro_v2.png")
sheet.save(out)
print("saved", os.path.relpath(out, HERE), sheet.size, "frames", len(cells))
