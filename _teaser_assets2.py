# -*- coding: utf-8 -*-
"""Проверка ассетов для правки тизера: размеры кадров и клипов."""
import os, subprocess, json
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FF = "/home/ivan/.nanobot/workspace/.probe/.lib/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
GEN = os.path.join(HERE, "assets", "gen")

def psize(p):
    if not os.path.exists(p):
        return "НЕТ"
    im = Image.open(p)
    return f"{im.width}x{im.height} {im.mode} {os.path.getsize(p)//1024}K"

def vinfo(p):
    if not os.path.exists(p):
        return "НЕТ"
    r = subprocess.run([FF, "-hide_banner", "-i", p], capture_output=True, text=True)
    lines = [l.strip() for l in r.stderr.splitlines() if "Stream" in l or "Duration" in l]
    return " | ".join(lines)

for n in ("logo_a_0.jpg", "logo_b_0.jpg", "kate_reception_vn_0.png",
          "ok_space_station_0.jpg", "ok_reception_fix2_0.jpg", "ok_x_kate_moon_0.jpg"):
    print(f"{n:28s}", psize(os.path.join(GEN, n)))

print()
for n in ("i2v_ship_0.mp4", "i2v_station_0.mp4", "i2v_kate_suit_0.mp4"):
    print(f"{n:24s}", vinfo(os.path.join(GEN, "vid", n)))

print()
print("joined :", vinfo(os.path.join(HERE, ".tmp_intro3", "joined.mp4")))
print("out16  :", vinfo(os.path.join(HERE, "out", "avm_v3_epic.mp4")))
print("out09  :", vinfo(os.path.join(HERE, "out", "avm_v3_epic_9x16.mp4")))
print()
print("audio:", [f for f in sorted(os.listdir(os.path.join(HERE, "assets", "audio")))
                 if f.startswith("theme_")])
