#!/usr/bin/env python3
"""Считает, сколько ОПЕРАТИВНОЙ памяти держит предзагрузка vn2:
декодированные битмапы картинок (W*H*4) + blob'ы аудио/видео (сжатые байты)."""
import os, json, glob
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VN = os.path.join(HERE, "vn2")

rows = []
tot_dec = tot_file = 0
for p in sorted(glob.glob(os.path.join(VN, "img", "**", "*"), recursive=True)):
    if not os.path.isfile(p):
        continue
    ext = p.rsplit(".", 1)[-1].lower()
    if ext not in ("webp", "png", "jpg", "jpeg"):
        continue
    sz = os.path.getsize(p)
    try:
        with Image.open(p) as im:
            w, h = im.size
    except Exception:
        w = h = 0
    dec = w * h * 4
    rows.append((dec, sz, w, h, os.path.relpath(p, VN)))
    tot_dec += dec
    tot_file += sz

rows.sort(reverse=True)
print("%-34s %5s %-11s %9s %9s" % ("file", "MPix", "size", "decoded", "on disk"))
for dec, sz, w, h, rel in rows:
    print("%-34s %5.1f %-11s %8.1fM %8.2fM" % (rel, w * h / 1e6, "%dx%d" % (w, h), dec / 1e6, sz / 1e6))
print("-" * 76)
print("картинок: %d   декодировано: %.1f МБ   на диске: %.1f МБ" % (len(rows), tot_dec / 1e6, tot_file / 1e6))

# аудио и видео — только сжатые байты в blob'ах
aud = vid = 0
na = nv = 0
for p in glob.glob(os.path.join(VN, "audio", "**", "*"), recursive=True) + glob.glob(os.path.join(VN, "img", "**", "*.mp4"), recursive=True):
    if os.path.isfile(p):
        aud += os.path.getsize(p); na += 1
for p in glob.glob(os.path.join(VN, "**", "*.mp4"), recursive=True):
    if os.path.isfile(p) and "/img/" not in p:
        vid += os.path.getsize(p); nv += 1
print("аудио: %d файлов, %.1f МБ blob   видео: %d, %.1f МБ" % (na, aud / 1e6, nv, vid / 1e6))
print("ИТОГО в RAM после полной предзагрузки: ~%.0f МБ" % ((tot_dec + aud + vid) / 1e6))

# что реально попадает в предзагрузку: только то, что в content.js
cj = os.path.join(VN, "content.js")
txt = open(cj, encoding="utf-8").read()
import re
urls = set(re.findall(r"[\"']([^\"']+\.(?:webp|png|jpg|mp3|mp4))[\"']", txt))
print("\nurl'ов в content.js: %d" % len(urls))
dec2 = 0
for u in urls:
    rel = u.replace("../", "")
    p = os.path.join(VN, rel) if not rel.startswith("vn2/") else os.path.join(HERE, rel)
    if not os.path.exists(p):
        continue
    if p.lower().endswith((".webp", ".png", ".jpg")):
        try:
            with Image.open(p) as im:
                dec2 += im.size[0] * im.size[1] * 4
        except Exception:
            pass
    else:
        dec2 += os.path.getsize(p)
print("из них в памяти: ~%.0f МБ" % (dec2 / 1e6))
