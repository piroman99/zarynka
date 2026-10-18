# -*- coding: utf-8 -*-
"""Разбор тизера avm_v3_epic.mp4: длительность + лист кадров каждые 2 с."""
import os, subprocess, json
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FF = "/home/ivan/.nanobot/workspace/.probe/.lib/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
SRC = os.path.join(HERE, "out", "avm_v3_epic.mp4")
TMP = os.path.join(HERE, ".tmp_avmcheck")
os.makedirs(TMP, exist_ok=True)

# длительность
r = subprocess.run([FF, "-i", SRC], capture_output=True, text=True)
for line in r.stderr.splitlines():
    if "Duration" in line or "Stream #" in line:
        print(line.strip())

def font(sz):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", sz)

# кадры каждые 2 с
for f in os.listdir(TMP):
    if f.endswith(".png"):
        os.remove(os.path.join(TMP, f))
subprocess.run([FF, "-y", "-i", SRC, "-vf", "fps=1/2", "-frames:v", "24",
                os.path.join(TMP, "f_%02d.png")], capture_output=True, text=True)
files = sorted(f for f in os.listdir(TMP) if f.startswith("f_"))
print("кадров:", len(files))

cols, CW = 3, 620
ims = [(("%.0f s" % (i * 2)), Image.open(os.path.join(TMP, f))) for i, f in enumerate(files)]
CH = round(CW * ims[0][1].height / ims[0][1].width)
rows = (len(ims) + cols - 1) // cols
PAD, LBL = 12, 28
sheet = Image.new("RGB", (cols * CW + (cols + 1) * PAD, rows * (CH + LBL + PAD) + PAD), (18, 20, 26))
d = ImageDraw.Draw(sheet)
fnt = font(20)
for i, (lab, im) in enumerate(ims):
    rr, cc = divmod(i, cols)
    x = PAD + cc * (CW + PAD)
    y = PAD + rr * (CH + LBL + PAD)
    d.text((x, y), "avm_v3_epic  t=" + lab, fill=(235, 232, 226), font=fnt)
    sheet.paste(im.resize((CW, CH), Image.LANCZOS), (x, y + LBL))
out = os.path.join(HERE, "assets", "review", "review_102_teaser_sheet.png")
sheet.save(out)
print("saved", os.path.relpath(out, HERE), sheet.size)
