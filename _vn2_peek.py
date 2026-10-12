# -*- coding: utf-8 -*-
"""Кроп тулбара/навигации из скриншотов vn2 (проверка вида тумблеров, стрелок
и того, что тулбар ДОСТУПЕН на титуле)."""
import os, glob, subprocess
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*', 'chrome-linux*', 'chrome'))[0]
IDX = os.path.join(HERE, 'vn2', 'index.html')
REV = os.path.join(HERE, 'assets', 'review')


def shot(url_q, out):
    p = os.path.join(REV, out)
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                    '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                    '--virtual-time-budget=4000', '--screenshot=' + p,
                    'file://' + IDX + '?' + url_q], capture_output=True, text=True, timeout=90)
    return p


# титул с включённым «Авто» (проверяем, что кнопка своя и красная на титуле)
shot('node=0&auto=1&instant=1&text=1&voice=0&music=0', 'review_75_vn2_title_auto.png')


def crop(src, box, out, scale=3):
    im = Image.open(os.path.join(REV, src)).convert('RGB')
    c = im.crop(box).resize(((box[2] - box[0]) * scale, (box[3] - box[1]) * scale), Image.LANCZOS)
    c.save(os.path.join(REV, out))
    print(out, c.size)


crop('review_75_vn2_title_auto.png', (820, 6, 1280, 74), 'review_75_vn2_tools_title_on.png')
crop('review_75_vn2_title_auto.png', (0, 0, 1280, 720), 'review_75_vn2_title_auto_full.png', 1)
crop('review_70_vn2_kate_sergey.png', (0, 250, 120, 480), 'review_70_vn2_peek_prev.png')
crop('review_70_vn2_kate_sergey.png', (1170, 250, 1280, 480), 'review_70_vn2_peek_next.png')
crop('review_70_vn2_auto_on.png', (820, 6, 1280, 74), 'review_70_vn2_peek_tools_auto.png')
crop('review_70_vn2_kate_n.png', (820, 6, 1280, 74), 'review_70_vn2_peek_tools_off.png')

tiles = ['review_75_vn2_tools_title_on.png', 'review_70_vn2_peek_tools_auto.png',
         'review_70_vn2_peek_tools_off.png', 'review_70_vn2_peek_prev.png',
         'review_70_vn2_peek_next.png']
ims = [Image.open(os.path.join(REV, t)).convert('RGB') for t in tiles]
W = max(i.width for i in ims); H = sum(i.height for i in ims)
sheet = Image.new('RGB', (W, H), (8, 10, 14))
y = 0
for i in ims:
    sheet.paste(i, (0, y)); y += i.height
sheet.save(os.path.join(REV, 'review_74_vn2_nav_tools.png'))
print('SHEET', sheet.size)
