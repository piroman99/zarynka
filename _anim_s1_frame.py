# -*- coding: utf-8 -*-
"""Кадр из пересобранного аниматика на участке S1 (t=11.5 c) — проверка, что новый мок вошёл."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.join(HERE, "..", "..", ".probe", ".lib", "imageio_ffmpeg", "binaries",
                  "ffmpeg-linux-x86_64-v7.0.2")
FF = os.path.abspath(FF)
src = os.path.join(HERE, "out", "prolog_animatic_draft.mp4")
dst = os.path.join(HERE, "assets", "review", "review_57b_animatic_s1_frame.png")
p = subprocess.run([FF, "-y", "-ss", "11.5", "-i", src, "-frames:v", "1", dst],
                   capture_output=True, text=True)
print("rc", p.returncode, os.path.exists(dst), os.path.getsize(dst) if os.path.exists(dst) else 0)
print(p.stderr[-400:])
