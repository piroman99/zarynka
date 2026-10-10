# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import os
p = "assets/orig/za smile.png"
im = Image.open(p).convert("RGBA")
print("size", im.size)
# bbox of non-transparent
bb = im.getbbox()
print("bbox", bb)
# checkerboard backdrop + sprite at ~2x height
H = 900
s = H / im.height
im2 = im.resize((int(im.width * s), H), Image.LANCZOS)
sheet = Image.new("RGB", (im2.width + 520, H), (200, 205, 210))
d = ImageDraw.Draw(sheet)
for y in range(0, H, 24):
    for x in range(0, sheet.width, 24):
        if (x // 24 + y // 24) % 2:
            d.rectangle([x, y, x + 23, y + 23], fill=(170, 176, 182))
sheet.paste(im2, (0, 0), im2)
# torso zoom (upper 45%)
tz = im.crop((0, 0, im.width, int(im.height * 0.5)))
tz = tz.resize((int(tz.width * (H * 0.9) / tz.height), int(H * 0.9)), Image.LANCZOS)
sheet.paste(tz, (im2.width + 10, 20), tz)
sheet.save("out/_sprite_inspect.png")
print("saved out/_sprite_inspect.png", sheet.size)
