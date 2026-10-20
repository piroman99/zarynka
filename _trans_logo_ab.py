# -*- coding: utf-8 -*-
"""A/B: значок в перехоже — КРУГ (как сейчас) против ПЯТИУГОЛЬНИКА (жетон).

Собирает лист assets/review/review_116_trans_logo_ab.png на тёмном фоне перехода,
чтобы Иван выбрал форму одним взглядом (0 ₽, только локальная сборка).
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
W, H, PAD = 1600, 620, 24


def on_dark(canvas, img, box, glow=True):
    """Вписать картинку в тёмный кадр box=(x, y, w, h) с золотым свечением.
    canvas — ОБЩЕЕ полотно (иначе правая половина закрасит левую)."""
    x, y, w, h = box
    im = img.copy()
    im.thumbnail((w, h), Image.LANCZOS)
    px, py = x + (w - im.width) // 2, y + (h - im.height) // 2
    if glow:
        g = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        g.paste((255, 214, 150, 80), (px, py), im.split()[3])
        g = g.filter(ImageFilter.GaussianBlur(20))
        canvas.alpha_composite(g)
    canvas.paste(im, (px, py), im)
    return canvas


circle = Image.open(os.path.join(HERE, 'vn2', 'img', 'logo.png')).convert('RGBA')
penta = Image.open(os.path.join(HERE, 'assets', 'gen', 'znachek_k1.png')).convert('RGBA')

sheet = Image.new('RGBA', (W, H), (7, 8, 12, 255))
on_dark(sheet, circle, (PAD, 70, W // 2 - 2 * PAD, H - 140))
on_dark(sheet, penta, (W // 2 + PAD, 70, W // 2 - 2 * PAD, H - 140))

d = ImageDraw.Draw(sheet)
f = ImageFont.truetype(FONT, 30)
fs = ImageFont.truetype(FONT, 22)
for x, t, sub in ((W // 4, 'КРУГ', 'как на титуле — сейчас в сборке'),
                  (W * 3 // 4, 'ПЯТИУГОЛЬНИК', 'жетон-значок из пролога')):
    tw = d.textlength(t, font=f)
    d.text((x - tw / 2, H - 92), t, font=f, fill=(238, 232, 220, 255))
    sw = d.textlength(sub, font=fs)
    d.text((x - sw / 2, H - 52), sub, font=fs, fill=(170, 165, 155, 255))
d.line([(W // 2, 40), (W // 2, H - 110)], fill=(60, 58, 54, 255), width=2)

out = os.path.join(HERE, 'assets', 'review', 'review_116_trans_logo_ab.png')
sheet.convert('RGB').save(out)
a = np.asarray(sheet.convert('L'), dtype=np.float32) / 255.0
print('углы кадра: %.3f %.3f | центр левой половины %.3f, правой %.3f'
      % (a[3, 3], a[-4, -4], a[H // 2, W // 4], a[H // 2, W * 3 // 4]))
print('->', out)
