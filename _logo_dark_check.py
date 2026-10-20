# -*- coding: utf-8 -*-
"""Как круглое лого выглядит на тёмном фоне перехода (свечения углов быть не должно)."""
import os
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
lg = Image.open(os.path.join(HERE, 'vn2', 'img', 'logo.png')).convert('RGBA')
W, H = 640, 400
bg = Image.new('RGBA', (W, H), (7, 8, 12, 255))
# мягкое золотое свечение под лого (как drop-shadow в CSS)
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
mask = lg.split()[3].resize((162, 162), Image.LANCZOS)
glow.paste((255, 214, 150, 90), (W // 2 - 81, H // 2 - 81), mask)
glow = glow.filter(ImageFilter.GaussianBlur(18))
bg = Image.alpha_composite(bg, glow)
small = lg.resize((162, 162), Image.LANCZOS)
bg.paste(small, (W // 2 - 81, H // 2 - 81), small)
out = os.path.join(HERE, 'assets', 'review', 'review_116_logo_round_on_dark.png')
bg.convert('RGB').save(out)
a = np.asarray(bg.convert('L'), dtype=np.float32) / 255.0
# проверка: углы кадра должны остаться тёмными
print('углы (яркость): %.3f %.3f %.3f %.3f' % (a[3, 3], a[3, -4], a[-4, 3], a[-4, -4]))
print('центр: %.3f' % a[H // 2, W // 2])
print('->', out)
