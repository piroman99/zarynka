# -*- coding: utf-8 -*-
"""Числовая проверка скриншотов оглавления (я PNG не вижу — только цифры):
не пустой ли кадр, сколько светлых «текстовых» полос по вертикали."""
import os
import sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
for name in ("toc_desktop.png", "toc_progress.png", "toc_mobile.png"):
    p = os.path.join(HERE, "_sat", name)
    if not os.path.exists(p):
        print(name, "НЕТ ФАЙЛА")
        continue
    im = Image.open(p).convert("L")
    w, h = im.size
    px = list(im.getdata())
    mean = sum(px) / len(px)
    # строки, где есть заметно светлые пиксели (текст/кнопки)
    rows = []
    for y in range(h):
        row = px[y * w:(y + 1) * w]
        if max(row) > 150:
            rows.append(y)
    bands = 0
    prev = -10
    for y in rows:
        if y - prev > 3:
            bands += 1
        prev = y
    print("%-18s %dx%d средняя яркость %.1f светлых полос %d" % (name, w, h, mean, bands))
