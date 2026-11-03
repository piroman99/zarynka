# -*- coding: utf-8 -*-
"""Два варианта полосы лозунга на стенде кадра 11-A (мок 2400x1350 -> 1672x941)."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
OUT = os.path.join(HERE, '_sat')
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
CREAM = (246, 238, 222)
WARM = (252, 226, 170)
RED = (168, 40, 34)
FW, FH = 2400, 1350
L1, L2 = 'МАРС — ДЕЛО ОБЩЕЕ!', 'ДАЁШЬ МАРС ДЛЯ ВСЕХ!'

im0 = Image.open(os.path.join(GEN, 's5a_a__gpt-image-2_0.png')).convert('RGB')


def band_mock(band, s1, s2, gap, out, blur=10, alpha=232):
    base = im0.resize((FW, FH), Image.LANCZOS)
    ov = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle(band, radius=20, fill=RED + (alpha,))
    ov = ov.filter(ImageFilter.GaussianBlur(blur))
    base = Image.alpha_composite(base.convert('RGBA'), ov).convert('RGB')
    d = ImageDraw.Draw(base)
    cx = (band[0] + band[2]) / 2
    total = s1 + gap + s2
    y0 = (band[1] + band[3]) / 2 - total / 2
    d.text((cx, y0), L1, font=ImageFont.truetype(GOTHIC, s1), fill=CREAM, anchor='ma')
    d.text((cx, y0 + s1 + gap), L2, font=ImageFont.truetype(GOTHIC, s2), fill=WARM, anchor='ma')
    p = os.path.join(OUT, out)
    base.resize((1672, 941), Image.LANCZOS).save(p)
    print('saved', p, 'band', band, 'sizes', s1, s2)


# V1 — большой плакат на весь стенд (плотная заливка, текст по центру)
band_mock((1500, 367, 2244, 902), 62, 58, 22, 's5a_band_v1.png')
# V2 — узкая полоса-перетяжка с крупным текстом
band_mock((1460, 560, 2284, 810), 72, 60, 26, 's5a_band_v2.png')
