# -*- coding: utf-8 -*-
"""Лист на согласование: база + новые эмоции Сергея (в движке и крупно)."""
import os, glob, subprocess
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
IDX = os.path.join(HERE, 'vn2', 'index.html')
OUT = os.path.join(HERE, '.tmp_vo')
GEN = os.path.join(HERE, 'assets', 'gen')
REV = os.path.join(HERE, 'assets', 'review')
os.makedirs(OUT, exist_ok=True)

# 1) крупно: база / smile / concerned
faces = [('база neutral', os.path.join(GEN, 'sergey_eng_old__flux-2_0.jpg')),
         ('smile (gpt-image-2)', os.path.join(GEN, 'sergey_smile_0.png')),
         ('concerned (gpt-image-2)', os.path.join(GEN, 'sergey_concerned_0.png'))]
TW = 620
tiles = []
for label, p in faces:
    im = Image.open(p).convert('RGB')
    w, h = im.size
    f = im.crop((int(w * .22), int(h * .04), int(w * .78), int(h * .40)))
    f = f.resize((TW, int(f.height * TW / f.width)), Image.LANCZOS)
    tiles.append((label, f))
th = tiles[0][1].height

# 2) в движке: страницы 8 / 18 / 49
shots = [(8, 'в движке: p08 neutral'), (18, 'в движке: p18 concerned'),
         (49, 'в движке: p49 smile')]
sfiles = []
for p, label in shots:
    out = os.path.join(OUT, 'emo_p%02d.png' % p)
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                    '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                    '--virtual-time-budget=6000', '--screenshot=' + out,
                    'file://' + IDX + '?instant=1&node=9&page=%d&text=1&voice=0&music=0' % p],
                   capture_output=True, text=True, timeout=120)
    sfiles.append((label, out))
    print(p, 'ok')

cw, ch = 640, 360
sheet = Image.new('RGB', (TW * 3, th + 26 + ch), (12, 14, 20))
d = ImageDraw.Draw(sheet)
for i, (label, im) in enumerate(tiles):
    sheet.paste(im, (i * TW, 26))
    d.text((i * TW + 8, 8), label, fill=(255, 255, 255))
for i, (label, f) in enumerate(sfiles):
    im = Image.open(f).convert('RGB').resize((cw, ch), Image.LANCZOS)
    y = th + 26
    sheet.paste(im, (i * cw, y))
    d.rectangle([i * cw, y, i * cw + cw - 1, y + ch - 1], outline=(40, 44, 56))
    d.rectangle([i * cw, y, i * cw + 230, y + 18], fill=(0, 0, 0))
    d.text((i * cw + 6, y + 4), label, fill=(255, 255, 255))
p = os.path.join(REV, 'review_78_sergey_emo_ok.png')
sheet.save(p)
print(p, sheet.size)
