# -*- coding: utf-8 -*-
"""Длительности сегментов закадра пролога (WAV -> сек) + оценка сценария."""
import os, wave, json
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "assets", "audio", "vo_prolog")
tot = 0.0
rows = []
for name in ("s1", "s2", "s3", "s4", "s5", "s6"):
    p = os.path.join(D, name + "_0.wav")
    if not os.path.exists(p):
        print("нет файла:", name); continue
    with wave.open(p, "rb") as w:
        dur = w.getnframes() / float(w.getframerate())
    tot += dur
    rows.append((name, dur))
    print(f"{name}: {dur:6.2f} c")
print(f"\nсумма VO: {tot:.2f} c   (+P0 8 c = клип {tot+8:.1f} c)")
