# -*- coding: utf-8 -*-
"""Проверка ветки TRANS_EMBLEM=penta: как пятиугольник ляжет в кадр перехода.

Пишет assets/review/review_116_trans_logo_penta.png (тёмный кадр 640x400, как #trans).
"""
import os
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')

emb = Image.open(os.path.join(GEN, 'znachek_k1.png')).convert('RGBA')
emb = emb.crop(emb.split()[3].getbbox())
side = max(emb.size)
sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
sq.paste(emb, ((side - emb.width) // 2, (side - emb.height) // 2), emb)
sq = sq.resize((512, 512), Image.LANCZOS)

W, H, SZ = 640, 400, 190
canvas = Image.new('RGBA', (W, H), (7, 8, 12, 255))
g = Image.new('RGBA', (W, H), (0, 0, 0, 0))
m = sq.split()[3].resize((SZ, SZ), Image.LANCZOS)
g.paste((255, 214, 150, 80), (W // 2 - SZ // 2, H // 2 - SZ // 2), m)
canvas.alpha_composite(g.filter(ImageFilter.GaussianBlur(20)))
sm = sq.resize((SZ, SZ), Image.LANCZOS)
canvas.paste(sm, (W // 2 - SZ // 2, H // 2 - SZ // 2), sm)
out = os.path.join(HERE, 'assets', 'review', 'review_116_trans_logo_penta.png')
canvas.convert('RGB').save(out)
print('пента: исходник обрезан до', sq.size, '-> ', out)
