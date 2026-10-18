# -*- coding: utf-8 -*-
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.new('RGB', (400, 200), (255, 255, 255))
d = ImageDraw.Draw(im)
f = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Bold.ttf', 160)
d.text((200, 100), 'K', font=f, fill=(0, 0, 0), anchor='mm')
p = os.path.join(HERE, 'assets', 'review', '_probe_letter.png')
im.save(p)
print(p)
