# -*- coding: utf-8 -*-
"""Из чего делать кадр «лунной базы»: сравнить арт (1344x768) с реальными кадрами тизера.

Тизер `out/avm_v3_epic.mp4` — 1920x1080, I2V-клипы. Если его кадр резче апскейла арта,
базу лучше брать оттуда. Меряем: разрешение, резкость (дисперсия лапласиана), шум,
и делаем лист-сравнение в нативном размере.
"""
import glob
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries',
                  'ffmpeg-linux-x86_64-v7.0.2')
OUT = os.path.join(HERE, '.tmp_vo', 'avm')
os.makedirs(OUT, exist_ok=True)

VID = os.path.join(HERE, 'out', 'avm_v3_epic.mp4')
print('тизер:', os.path.getsize(VID), 'B')

# 1 кадр в секунду — хватит, чтобы найти клипы
subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-i', VID,
                '-vf', 'fps=1', os.path.join(OUT, 'f_%03d.png')],
               capture_output=True, text=True)
frames = sorted(glob.glob(os.path.join(OUT, 'f_*.png')))
print('кадров вытащено:', len(frames))


def sharp(im):
    a = np.asarray(im.convert('L')).astype(np.float32)
    k = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    from numpy.lib.stride_tricks import sliding_window_view
    w = sliding_window_view(a, (3, 3))
    lap = (w * k).sum(axis=(2, 3))
    return float(lap.var()), float(a.std())


rows = []
for p in frames:
    im = Image.open(p)
    s, sd = sharp(im)
    rows.append((os.path.basename(p), im.size, s, sd))

print('\n  кадр        размер        резкость   контраст')
for n, sz, s, sd in rows:
    print('  %-11s %dx%d   %8.1f   %6.1f' % (n, sz[0], sz[1], s, sd))

# арт из тизера: как есть и после апскейла до 1920
art = Image.open(os.path.join(HERE, 'assets/gen/ok_space_station_0.jpg')).convert('RGB')
up = art.resize((1920, 1080), Image.LANCZOS)
s0, sd0 = sharp(up)
print('\nарт ok_space_station 1344x768 -> апскейл 1920x1080: резкость %.1f, контраст %.1f'
      % (s0, sd0))
sA, sdA = sharp(art)
print('арт как есть 1344x768:                              резкость %.1f, контраст %.1f' % (sA, sdA))

# лист: 6 самых резких кадров тизера + апскейл арта, кропы 640x360 из центра
best = sorted(rows, key=lambda r: -r[2])[:6]
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
cw, chh, pad, lab = 640, 360, 8, 20
cols = 2
cells = [('тизер ' + n, os.path.join(OUT, n)) for n, _, _, _ in best]
cells.append(('арт 1344 -> 1920 (LANCZOS)', None))
Hh = ((chh + lab + pad) * ((len(cells) + cols - 1) // cols)) + pad
cv = Image.new('RGB', (cw * cols + pad * (cols + 1), Hh), (14, 16, 22))
d = ImageDraw.Draw(cv)
for i, (labt, p) in enumerate(cells):
    if p is None:
        im = up.crop((640, 360, 1280, 720))
    else:
        im = Image.open(p).convert('RGB').crop((640, 360, 1280, 720))
    x = pad + (i % cols) * (cw + pad)
    y = pad + (i // cols) * (chh + lab + pad)
    cv.paste(im, (x, y))
    d.text((x, y + chh + 2), labt, fill=(216, 220, 228), font=f)
o = os.path.join(HERE, '_sat', 'sheet_station_src.png')
cv.save(o)
print('\nлист (кропы 640x360 в нативном масштабе):', o, cv.size)
