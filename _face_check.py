# -*- coding: utf-8 -*-
"""Кроп лица из пилота — проверить, похожа ли Екатерина на авторский спрайт 2016."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
src = Image.open(os.path.join(HERE, "assets/pilot/pilot_s_enter_0.png")).convert("RGB")
W, H = src.size
print("pilot", src.size)
# ищем фигуру в центре: берём центральную треть по ширине, верхнюю половину
box = (int(W * 0.34), int(H * 0.10), int(W * 0.66), int(H * 0.72))
crop = src.crop(box)
crop.save(os.path.join(HERE, "assets/pilot/_face.png"))
print("crop", crop.size)

ref = Image.open(os.path.join(HERE, "assets/src/caccf3b4ebc5.png")).convert("RGB")
rbox = (0, 0, ref.width, int(ref.height * 0.30))
ref = ref.crop(rbox)
h = 620
a = crop.resize((round(crop.width * h / crop.height), h), Image.LANCZOS)
c = ref.resize((round(ref.width * h / ref.height), h), Image.LANCZOS)
sheet = Image.new("RGB", (a.width + c.width + 24, h), (24, 24, 28))
sheet.paste(c, (0, 0))
sheet.paste(a, (c.width + 24, 0))
out = os.path.join(HERE, "assets/pilot/face_compare.png")
sheet.save(out)
print(out, sheet.size)
