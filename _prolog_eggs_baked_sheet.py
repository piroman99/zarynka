# -*- coding: utf-8 -*-
"""Лист-выборка из пересобранного аниматика: где видны вкомпонованные пасхалки."""
import os, subprocess
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.abspath(os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg',
                                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2'))
SRC = os.path.join(HERE, 'out', 'prolog_animatic_draft.mp4')
REV = os.path.join(HERE, 'assets', 'review')
TMP = os.path.join(HERE, '.tmp_diag'); os.makedirs(TMP, exist_ok=True)
GOTH = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'

ITEMS = [(2.0, 'P0 · ребро — гравировка «ЛМД» (микро)'),
         (12.0, 'S1 · котобус мелом на стене'),
         (28.0, 'S2 · транспорт-2061, маршрут «410»'),
         (79.0, 'S6 · часы 06:07 на стене приёмной')]

CW = 900
imgs = []
for t, cap in ITEMS:
    p = os.path.join(TMP, 'sel_%.1f.png' % t)
    subprocess.run([FF, '-y', '-ss', str(t), '-i', SRC, '-frames:v', '1', p],
                   capture_output=True, text=True)
    im = Image.open(p).convert('RGB').resize((CW, round(720 * CW / 1280)), Image.LANCZOS)
    imgs.append((im, cap))

pad, caph, hdr = 20, 46, 80
H = hdr + sum(im.height + caph + pad for im, _ in imgs) + pad
canvas = Image.new('RGB', (CW + 2 * pad, H), (13, 14, 19))
d = ImageDraw.Draw(canvas)
d.text((pad, 16), '«ЗАРЯНКА» · пролог — вкомпонованные пасхалки (аниматик пересобран)',
       font=ImageFont.truetype(GOTH, 30), fill=(226, 186, 104))
d.text((pad, 50), 'Кадры из out/prolog_animatic_draft.mp4 (черновик, 0 ₽).',
       font=ImageFont.truetype(LATO_B, 20), fill=(200, 206, 220))
y = hdr
for im, cap in imgs:
    canvas.paste(im, (pad, y))
    d.rectangle([pad, y, pad + im.width, y + im.height], outline=(60, 62, 74))
    d.text((pad, y + im.height + 6), cap, font=ImageFont.truetype(LATO_B, 24), fill=(240, 236, 228))
    y += im.height + caph + pad
canvas.save(os.path.join(REV, 'review_64_prolog_eggs_baked.png'))
print('saved review_64', canvas.size)
