# -*- coding: utf-8 -*-
"""Проверка выреза Старика: ореол по кромке альфы + лист review.
1) кромка (0<alpha<250): доля пикселей, близких к цвету фона (197,196,195);
2) сборка: спрайт на синем, на фоне приёмной, зум кромки -> assets/review/.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SPR = os.path.join(HERE, 'assets', 'sprites', 'starik_stern.png')
BG = os.path.join(HERE, 'vn2', 'img', 'bg', 'reception.webp')
OUT = os.path.join(HERE, 'assets', 'review')
FONT = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
f = lambda s: ImageFont.truetype(FONT, s)

im = Image.open(SPR).convert('RGBA')
px = im.load()
w, h = im.size
edge = 0
edge_bgish = 0
for y in range(h):
    for x in range(w):
        r, g, b, a = px[x, y]
        if 0 < a < 250:
            edge += 1
            if abs(r - 197) <= 14 and abs(g - 196) <= 14 and abs(b - 195) <= 14:
                edge_bgish += 1
print('sprite', w, h, 'edge px', edge, 'bgish on edge %.1f%%' % (100.0 * edge_bgish / max(edge, 1)))

# --- лист
W, H = 1500, 950
sheet = Image.new('RGB', (W, H), (16, 18, 24))
d = ImageDraw.Draw(sheet)
d.text((16, 10), 'Старик — вырез спрайта (starik_stern.png)', font=f(26), fill=(230, 200, 150))

def fit(src, box):
    bw, bh = box
    r = min(bw / src.width, bh / src.height)
    return src.resize((max(1, int(src.width * r)), max(1, int(src.height * r))), Image.LANCZOS)

# 1) на синем
blue = Image.new('RGB', (480, 860), (24, 40, 120))
s1 = fit(im, (470, 850))
blue.paste(s1, ((480 - s1.width) // 2, 860 - s1.height), s1)
sheet.paste(blue, (16, 50))
d.text((16, 912), 'на синем', font=f(18), fill=(200, 200, 210))

# 2) на фоне приёмной (как в игре)
bg = Image.open(BG).convert('RGB').resize((480, 860), Image.LANCZOS)
s2 = fit(im, (470, 850))
bg.paste(s2, ((480 - s2.width) // 2, 860 - s2.height), s2)
sheet.paste(bg, (508, 50))
d.text((508, 910), 'на фоне приёмной', font=f(18), fill=(200, 200, 210))

# 3) зум кромки: голова (верх 0..30% высоты) на зелёном, 3x
head = im.crop((0, 0, w, int(h * 0.34)))
zoom = 2
hz = head.resize((head.width * zoom, head.height * zoom), Image.NEAREST)
green = Image.new('RGB', hz.size, (0, 160, 90))
green.paste(hz, (0, 0), hz)
sheet.paste(fit(green, (470, 850)), (1000, 50))
d.text((1000, 910), 'зум кромки 2x', font=f(18), fill=(200, 200, 210))

p = os.path.join(OUT, 'review_131_starik_sprite.png')
sheet.save(p)
print('->', os.path.relpath(p, HERE), sheet.size)
