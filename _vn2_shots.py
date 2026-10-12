# -*- coding: utf-8 -*-
"""Скриншоты vn2 (headless chromium) + контактный лист. -> assets/review/review_70_vn2_*.png"""
import os, subprocess, glob
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*', 'chrome-linux*', 'chrome'))[0]
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
REV = os.path.join(HERE, 'assets', 'review')
IDX = os.path.join(HERE, 'vn2', 'index.html')

SHOTS = [
    ('title',       'node=0&text=1&voice=0&music=0'),
    ('s1',          'node=2&text=1&voice=0&music=0'),
    ('s3',          'node=4&text=1&voice=0&music=0'),
    ('s5',          'node=6&text=1&voice=0&music=0'),
    ('s7',          'node=8&text=1&voice=0&music=0'),
    ('kate_n',      'node=9&page=0&text=1&voice=0&music=0'),
    ('kate_sergey', 'node=9&page=8&text=1&voice=0&music=0'),
    ('kate_kate',   'node=9&page=10&text=1&voice=0&music=0'),
    ('voice_off',   'node=9&page=10&text=0&voice=0&music=0'),
]


def shot(name, q):
    url = 'file://' + IDX + '?instant=1&' + q
    out = os.path.join(REV, 'review_70_vn2_%s.png' % name)
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                    '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                    '--virtual-time-budget=5000', '--screenshot=' + out, url],
                   capture_output=True, text=True, timeout=90)
    return out


for nm, q in SHOTS:
    shot(nm, q)
    print(nm, 'ok')

# кадр значка из mp4 (видео-узел headless не отдаёт) -> отдельная плитка
zn = os.path.join(REV, 'review_70_vn2_znakframe.png')
subprocess.run([FF, '-y', '-ss', '1.2', '-i', os.path.join(HERE, 'out', 'znak3d_rot_draft.mp4'),
                '-frames:v', '1', '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,'
                'pad=1280:720:(ow-iw)/2:(oh-ih)/2:black', zn], capture_output=True, text=True)

order = ['title', 'znakframe', 's1', 's3', 's5', 's7', 'kate_n', 'kate_sergey', 'kate_kate']
cw, ch, cols = 480, 270, 3
rows = (len(order) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cw, rows * ch), (10, 12, 18))
d = ImageDraw.Draw(sheet)
for i, nm in enumerate(order):
    f = os.path.join(REV, 'review_70_vn2_%s.png' % nm)
    im = Image.open(f).convert('RGB').resize((cw, ch), Image.LANCZOS)
    x, y = (i % cols) * cw, (i // cols) * ch
    sheet.paste(im, (x, y))
    d.rectangle([x, y, x + cw - 1, y + ch - 1], outline=(40, 44, 56))
    d.text((x + 8, y + 6), nm, fill=(255, 255, 255))
sheet.save(os.path.join(REV, 'review_70_vn2_sheet.png'))
print('SHEET', sheet.size)
