# -*- coding: utf-8 -*-
"""Кропает лист-рейтинг на 4 части, чтобы рассмотреть детали."""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "assets/rating/rating_sheet.png")
im = Image.open(p)
W, H = im.size
top = im.crop((0, 0, W, H // 2))
bot = im.crop((0, H // 2, W, H))
top.save(os.path.join(HERE, "assets/rating/_top.png"))
bot.save(os.path.join(HERE, "assets/rating/_bot.png"))
print("ok", im.size)
