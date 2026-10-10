# -*- coding: utf-8 -*-
"""Собрать два варианта AVM v3 (тёплая и эпичная музыка) из готовой склейки."""
import os, subprocess, glob
HERE = os.path.dirname(os.path.abspath(__file__))
FF = "/home/ivan/.nanobot/workspace/.probe/.lib/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
joined = os.path.join(HERE, ".tmp_intro3", "joined.mp4")
for tag in ("warm", "epic"):
    m = sorted(glob.glob(os.path.join(HERE, "assets", "audio", f"theme_{tag}_*")))
    m = [x for x in m if x.lower().endswith((".mp3", ".wav", ".m4a", ".ogg"))]
    if not m:
        print("нет музыки", tag); continue
    out = os.path.join(HERE, "out", f"avm_v3_{tag}.mp4")
    r = subprocess.run([FF, "-y", "-i", joined, "-i", m[0], "-c:v", "copy", "-c:a", "aac",
                        "-b:a", "192k", "-shortest", "-map", "0:v:0", "-map", "1:a:0", out],
                       capture_output=True, text=True)
    print(tag, "rc", r.returncode, os.path.relpath(out, HERE),
          os.path.getsize(out) if os.path.exists(out) else 0)
# кадры для контрольного листа
os.makedirs(os.path.join(HERE, ".tmp_diag"), exist_ok=True)
for t in (2.0, 5.0, 9.0, 13.0, 17.0, 21.0, 26.0, 30.0):
    dst = os.path.join(HERE, ".tmp_diag", f"v3_{int(t):02d}.png")
    subprocess.run([FF, "-y", "-ss", str(t), "-i", os.path.join(HERE, "out", "avm_v3_warm.mp4"),
                    "-frames:v", "1", "-vf", "scale=760:-1", dst], capture_output=True)
info = subprocess.run([FF, "-hide_banner", "-i", os.path.join(HERE, "out", "avm_v3_warm.mp4")],
                      capture_output=True, text=True).stderr
print([l.strip() for l in info.splitlines() if "Duration" in l])
