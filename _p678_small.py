# -*- coding: utf-8 -*-
"""Уменьшенные копии листа 6-8 для просмотра агентом."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(HERE, "_sat")

for name, w in (("sheet_p678.png", 760), ("sheet_p678_detail.png", 700)):
    im = Image.open(os.path.join(S, name)).convert("RGB")
    h = int(round(w * im.size[1] / im.size[0]))
    out = os.path.join(S, name.replace(".png", "_small.jpg"))
    im.resize((w, h), Image.LANCZOS).save(out, quality=88)
    print("saved", out, (w, h))
