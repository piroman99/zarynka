# -*- coding: utf-8 -*-
"""P0 — лист «гравировка МЕЛЬКОМ»: полоса кадров вращения вокруг 90° (t≈1.4 c) и макро рёбра.
Проверяем правку заказчика (2026-10-11): убрана ПАУЗА на ребре, «ЛМД» только мелькает.
Источник: out/znak3d_rot_draft.mp4 (пересобран). Выход: review_66_znak_flash.png
"""
import os, subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.abspath(os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg',
                                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2'))
SRC = os.path.join(HERE, 'out', 'znak3d_rot_draft.mp4')
REV = os.path.join(HERE, 'assets', 'review')
TMP = os.path.join(HERE, '.tmp_diag'); os.makedirs(TMP, exist_ok=True)
GOTH = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'

# 90° при t=1.4 c; берём плотную сетку вокруг, чтобы поймать «мелькание»
TS = [1.10, 1.30, 1.38, 1.40, 1.42, 1.50, 1.70]

# --- макро рёбра (из _znak3d.render при 90°)
src = open(os.path.join(HERE, '_znak3d.py')).read().split("if '--sheet' in sys.argv:")[0]
ns = {'__file__': os.path.join(HERE, '_znak3d.py'), '__name__': 'z3d'}
exec(compile(src, '_znak3d.py', 'exec'), ns)
render, RIB_TEXT = ns['render'], ns['RIB_TEXT']
import numpy as np
BIG = 4000
m = render(90, w=BIG, h=BIG)
arr = np.asarray(m)
fg = (np.abs(arr.astype(int) - np.array([6, 8, 18])).sum(axis=2) > 24)
ys, xs = np.where(fg)
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
print('ребро 90° в {0}px-рендере: w={1} h={2}'.format(BIG, x1 - x0 + 1, y1 - y0 + 1))
macro = m.crop((max(0, x0 - 40), max(0, y0 - 20), min(BIG, x1 + 40), min(BIG, y1 + 20)))
sc = 620 / macro.height
macro = macro.resize((max(1, int(macro.width * sc)), 620), Image.LANCZOS)

# --- полоса кадров
CW = 420
strip = []
for t in TS:
    p = os.path.join(TMP, 'flash_%.2f.png' % t)
    subprocess.run([FF, '-y', '-ss', '%.3f' % t, '-i', SRC, '-frames:v', '1', p],
                   capture_output=True, text=True)
    im = Image.open(p).convert('RGB').resize((CW, round(720 * CW / 1280)), Image.LANCZOS)
    strip.append((t, im))

PAD, HDR = 24, 128
rowh = strip[0][1].height
W = max(macro.width + 460 + 3 * PAD, len(strip) * (CW + 10) + PAD)
H = HDR + 40 + macro.height + 60 + rowh + 40 + PAD
sheet = Image.new('RGB', (W, H), (13, 14, 19))
d = ImageDraw.Draw(sheet)
d.text((PAD, 16), 'P0 · ГРАВИРОВКА «МЕЛЬКОМ» — паузы на ребре больше нет', font=ImageFont.truetype(GOTH, 34), fill=(226, 186, 104))
d.text((PAD, 60), 'Значок поворачивается 0°→180° сплошным проходом (0.6–2.3 c, в _prolog_animatic.py). '
                  'На 90° силуэт на миг становится тонким ребром — «%s» видно 1–2 кадра.' % RIB_TEXT,
       font=ImageFont.truetype(LATO_B, 21), fill=(206, 211, 230))
d.text((PAD, 90), 'Ниже: МАКРО рёбра (крупный 3D-рендер) — как «%s» читается, если дать наезд; '
                  'справа — полоса кадров из out/znak3d_rot_draft.mp4 вокруг 90°.' % RIB_TEXT,
       font=ImageFont.truetype(LATO_B, 21), fill=(150, 205, 150))

y = HDR + 40
sheet.paste(macro, (PAD, y))
d.rectangle([PAD - 1, y - 1, PAD + macro.width, y + macro.height], outline=(80, 82, 96))
d.text((PAD + macro.width + 24, y + 6), 'МАКРО РЕБРА 90°', font=ImageFont.truetype(LATO_B, 24), fill=(150, 205, 150))
d.text((PAD + macro.width + 24, y + 44), '«%s»' % RIB_TEXT, font=ImageFont.truetype(GOTH, 46), fill=(238, 214, 150))
d.text((PAD + macro.width + 24, y + 110),
       'физика рёбра: silhouette 0°→479 px,\n90°→~29 px (толщина), 180°→снова лицо.',
       font=ImageFont.truetype(LATO_B, 20), fill=(196, 202, 220), spacing=8)

yr = y + macro.height + 60
d.text((PAD, yr - 36), 'кадры вокруг 90° (t = 1.40 c):', font=ImageFont.truetype(LATO_B, 22), fill=(226, 186, 104))
x = PAD
for t, im in strip:
    sheet.paste(im, (x, yr))
    d.rectangle([x, yr, x + im.width, yr + im.height], outline=(70, 72, 86))
    d.text((x + 4, yr + im.height + 6), 't=%.2f c' % t, font=ImageFont.truetype(LATO_B, 20), fill=(220, 224, 236))
    x += CW + 10

out = os.path.join(REV, 'review_66_znak_flash.png')
sheet.save(out)
print('saved', os.path.relpath(out, HERE), sheet.size)
