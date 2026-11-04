# -*- coding: utf-8 -*-
"""Механические проверки CG: размер, соотношение, «не пусто», крупные плоские области."""
import os, sys
from PIL import Image, ImageStat
HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "assets", "gen")

files = sys.argv[1:] or [
    "cg_sad_a__gpt-image-2_0.png", "cg_sad_b__gpt-image-2_0.png", "cg_sad_c__gpt-image-2_0.png",
    "cg_sad_a__nano-banana-2.1_0.png", "cg_sad_b__nano-banana-2.1_0.png",
    "cg_sad_c__nano-banana-2.1_0.png",
]
for f in files:
    p = os.path.join(GEN, f)
    if not os.path.exists(p):
        print("%-34s нет файла" % f)
        continue
    im = Image.open(p).convert("RGB")
    st = ImageStat.Stat(im)
    px = im.resize((64, 36)).getdata()
    uniq = len(set(px))
    print("%-34s %dx%d ratio=%.3f  KB=%4d mean=%s uniq64=%d"
          % (f, im.width, im.height, im.width / im.height, os.path.getsize(p) // 1024,
             [round(v) for v in st.mean], uniq))
