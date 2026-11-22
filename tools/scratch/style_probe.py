# -*- coding: utf-8 -*-
"""Разбор стиля спрайта + параметры gpt-image-2 (image-to-image)."""
import json, pv
from PIL import Image

# 1) характеристики спрайта-эталона
for name in ("c66f332fa5c9.png", "caccf3b4ebc5.png"):
    p = "assets/src/" + name
    im = Image.open(p)
    print(name, im.size, im.mode)

# средний цвет (палитра) спрайта
im = Image.open("assets/src/c66f332fa5c9.png").convert("RGB")
im.thumbnail((64, 64))
px = list(im.getdata())
avg = tuple(sum(c[i] for c in px) // len(px) for i in range(3))
print("avg color:", avg)

# 2) capabilities gpt-image-2
print("\n=== capabilities gpt-image-2 ===")
try:
    caps = pv.capabilities("gpt-image-2")
    txt = json.dumps(caps, ensure_ascii=False)
    print(txt[:2500])
except Exception as e:
    print("ERR", e)
