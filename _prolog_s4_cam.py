# -*- coding: utf-8 -*-
"""S4 «двухбит одним кадром»: лист-сверка бит1 (широкий) → бит2 (наезд на Марс).
Математика НАЕЗДА = как в CSS: гомотетия с центром transform-origin (ox,oy) и масштабом S.
Здесь — просто кроп исходного кадра по обратному отображению."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'assets', 'final', 'prolog', 's4.png')
OUT = os.path.join(HERE, 'assets', 'review')
os.makedirs(OUT, exist_ok=True)

W, H = 1920, 1080
OX, OY = 0.44, 0.30            # точка наезда (Марс на панели) — доля кадра
S1, S2 = 1.0, 1.5             # бит1 широкий → бит2 наезд

FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def cam(im, S, ox=OX, oy=OY):
    """Симуляция CSS transform: scale(S) с transform-origin (ox,oy)."""
    w, h = im.size
    px, py = ox * w, oy * h
    x0 = px - px / S
    y0 = py - py / S
    x1 = px + (w - px) / S
    y1 = py + (h - py) / S
    return im.crop((round(x0), round(y0), round(x1), round(y1))).resize((w, h), Image.LANCZOS)


src = Image.open(SRC).convert('RGB')
b1 = cam(src, S1)
b2 = cam(src, S2)
b1.save(os.path.join(OUT, '_tmp_s4_beat1.png'))
b2.save(os.path.join(OUT, '_tmp_s4_beat2.png'))

# лист: два кадра друг под другом + подписи
scale = 0.5
sw, sh = int(W * scale), int(H * scale)
sheet = Image.new('RGB', (sw, sh * 2 + 24), (10, 12, 18))
sheet.paste(b1.resize((sw, sh), Image.LANCZOS), (0, 0))
sheet.paste(b2.resize((sw, sh), Image.LANCZOS), (0, sh + 24))
d = ImageDraw.Draw(sheet)
try:
    f = ImageFont.truetype(FONT, 26)
except Exception:
    f = ImageFont.load_default()
d.text((14, 8), 'БИТ 1 — широкий (S4, scale 1.0)', font=f, fill=(240, 230, 200))
d.text((14, sh + 32), 'БИТ 2 — наезд на Марс (scale %.1f @ %.0f%%,%.0f%%)' % (S2, OX * 100, OY * 100),
       font=f, fill=(240, 230, 200))
p = os.path.join(OUT, 'review_94_s4_cam.png')
sheet.save(p)
print('ok', os.path.relpath(p, HERE), sheet.size)
