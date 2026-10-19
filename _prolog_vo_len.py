# -*- coding: utf-8 -*-
"""Сколько времени в прологе занимает голос (он и задаёт темп авто-режима)."""
import os, glob, subprocess, json

HERE = os.path.dirname(os.path.abspath(__file__))
FF = glob.glob(os.path.join(HERE, "..", "..", ".probe", ".lib", "imageio_ffmpeg", "binaries", "ffmpeg*"))[0]
VO = os.path.join(HERE, "vn2", "audio", "vo")

total = 0.0
rows = []
for f in sorted(glob.glob(os.path.join(VO, "*.mp3"))):
    name = os.path.basename(f)
    if not name.startswith("s"):
        continue
    r = subprocess.run([FF, "-hide_banner", "-i", f], capture_output=True, text=True)
    dur = None
    for ln in r.stderr.splitlines():
        if "Duration:" in ln:
            hms = ln.split("Duration:")[1].split(",")[0].strip()
            h, m, s = hms.split(":")
            dur = int(h) * 3600 + int(m) * 60 + float(s)
            break
    if dur:
        total += dur
        rows.append((name, round(dur, 1)))

for n, d in rows:
    print(f"  {n}: {d}s")
print(f"\nстраниц пролога: {len(rows)}, голос всего: {total:.1f}s ({total/60:.2f} мин)")
print(f"если ускорить голос на 20%: {total*0.8:.1f}s (−{total*0.2:.1f}s)")
