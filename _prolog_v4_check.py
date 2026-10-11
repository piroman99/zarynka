# -*- coding: utf-8 -*-
"""Проверка v4-аниматика: длительность, наличие S7-хвоста и затемнения ПОСЛЕ речи.
Лист review_68: т=1/20/40/65/80/90/96/97.4 c.
"""
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

r = subprocess.run([FF, '-hide_banner', '-i', SRC], capture_output=True, text=True)
dur = [l.strip() for l in r.stderr.splitlines() if l.strip().startswith('Duration')]
print('DURATION:', dur[0] if dur else '?')

TS = [(1.0, 'P0 значок (грейд)'), (20.0, 'S1 подворотня'), (40.0, 'S2 Звёздный городок'),
      (60.0, 'S4/5 лозунг'), (80.0, 'S6 очередь (речь ещё идёт)'),
      (90.0, 'S7 ХВОСТ проходная (БЕЗ речи)'), (96.5, 'затемнение'), (97.4, 'почти чёрное')]
CW = 640
frames = []
for t, cap in TS:
    p = os.path.join(TMP, 'v4_%.1f.png' % t)
    subprocess.run([FF, '-y', '-ss', '%.3f' % t, '-i', SRC, '-frames:v', '1', p],
                   capture_output=True, text=True)
    im = Image.open(p).convert('RGB').resize((CW, round(1080 * CW / 1920)), Image.LANCZOS)
    frames.append((t, im, cap))

COLS = 2
PAD, HDR = 22, 108
CAPH = 40
rows = (len(frames) + COLS - 1) // COLS
fw, fh = frames[0][1].size
W = COLS * (fw + PAD) + PAD
H = HDR + rows * (fh + CAPH + PAD) + PAD
sheet = Image.new('RGB', (W, H), (13, 14, 19))
d = ImageDraw.Draw(sheet)
d.text((PAD, 16), '«ЗАРЯНКА» · пролог v4 — ГРЕЙД «тёплый архив» + ХВОСТ S7 + затемнение после речи',
       font=ImageFont.truetype(GOTH, 32), fill=(226, 186, 104))
d.text((PAD, 60), 'Речь кончается на S6 (87.6 c) → дальше молчаливый S7 «проходная·очередь» (10.4 c) '
                  '→ затемнение в самом конце. Всего 97.98 c.', font=ImageFont.truetype(LATO_B, 21),
       fill=(200, 206, 220))
for i, (t, im, cap) in enumerate(frames):
    cx = PAD + (i % COLS) * (fw + PAD)
    cy = HDR + (i // COLS) * (fh + CAPH + PAD)
    sheet.paste(im, (cx, cy))
    d.rectangle([cx, cy, cx + fw, cy + fh], outline=(70, 72, 86))
    d.text((cx + 4, cy + fh + 6), 't=%.1f c — %s' % (t, cap),
           font=ImageFont.truetype(LATO_B, 20), fill=(230, 226, 218))
out = os.path.join(REV, 'review_68_prolog_v4_check.png')
sheet.save(out)
print('saved', os.path.relpath(out, HERE), sheet.size)
