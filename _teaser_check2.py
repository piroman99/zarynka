# -*- coding: utf-8 -*-
"""Лист проверки после правки тизера: новые кадры + «до/после» астронавта + 9:16."""
import os, subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FF = "/home/ivan/.nanobot/workspace/.probe/.lib/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
TMP = os.path.join(HERE, ".tmp_avmcheck")
os.makedirs(TMP, exist_ok=True)
NEW = os.path.join(HERE, "out", "avm_v3_epic.mp4")
OLD = os.path.join(HERE, ".tmp_avm_bak", "avm_v3_epic.mp4")
VER = os.path.join(HERE, "out", "avm_v3_epic_9x16.mp4")


def frame(video, t, tag):
    p = os.path.join(TMP, f"{tag}_{t}.png")
    subprocess.run([FF, "-y", "-ss", str(t), "-i", video, "-frames:v", "1", p], capture_output=True)
    return Image.open(p).convert("RGB")


cells = [
    ("НОВОЕ  t=0.5 — лого в круге (диск с альфой)", frame(NEW, 0.5, "n")),
    ("НОВОЕ  t=16.5 — приёмная 16:9, комбинезон", frame(NEW, 16.5, "n")),
    ("НОВОЕ  t=27.6 — финальная карточка (лого в круге)", frame(NEW, 27.6, "n")),
    ("НОВОЕ  t=20.5 — астронавт: тёмный градиент", frame(NEW, 20.5, "n")),
    ("БЫЛО  t=20.5 — астронавт: размытые полосы", frame(OLD, 20.5, "o")),
    ("НОВОЕ 9:16  t=20.5", frame(VER, 20.5, "v")),
]

CW = 900
def fit(im):
    k = CW / im.width
    return im.resize((CW, round(im.height * k)), Image.LANCZOS)

cells = [(lab, fit(im)) for lab, im in cells]
LBL, PAD = 30, 14
rowh = max(c[1].height for c in cells)
sheet = Image.new("RGB", (2 * CW + 3 * PAD, 3 * (rowh + LBL + PAD) + PAD), (16, 18, 24))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 21)
for i, (lab, im) in enumerate(cells):
    r, c = divmod(i, 2)
    x = PAD + c * (CW + PAD)
    y = PAD + r * (rowh + LBL + PAD)
    d.text((x, y), lab, fill=(240, 236, 228), font=f)
    sheet.paste(im, (x, y + LBL))
out = os.path.join(HERE, "assets", "review", "review_107_teaser_fix_after.png")
sheet.save(out)
print("saved", os.path.relpath(out, HERE), sheet.size)

# крупно: угол карточки (нет белого квадрата?) и кадр астронавта
for tag, t, video in (("card", 1.2, NEW), ("kate", 20.5, NEW)):
    im = frame(video, t, "z")
    im.save(os.path.join(TMP, f"big_{tag}.png"))
print("big frames ok")
