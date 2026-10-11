#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Контрольный лист артов конкурса «Зарянка» (2061.su) — по полноценным файлам."""
import os, json
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'refs', 'contest_hi')
OUT = os.path.join(HERE, 'assets', 'review', 'review_26_contest.png')

VOTES = {'baba-katia': 31, 'ekaterina-ivanovna-zarianka': 208,
         'na-leto-k-babushke-zariantsy': 141, 'nauchnaia-programma': 59,
         'pochta-zarianke': 52, 'zarianka-13': 14, 'zarianka-14': 37,
         'zarianka-15': 108, 'zarianka-16': 20, 'zarianka-18': 16,
         'zdravstvui-babushka-katia': 26, 'zorianka': 12,
         'zoryanka2061': 21, 'zvezdnaia-babushka': 109}
AWARD = {'nauchnaia-programma': 'JURY', 'ekaterina-ivanovna-zarianka': 'VIEWER'}

mf = json.load(open(os.path.join(SRC, 'manifest.json'), encoding='utf-8'))
# схлопнуть work-дубли (та же работа, второй URL)
seen, items = set(), []
for x in mf:
    if x['slug'] in seen:
        continue
    seen.add(x['slug']); items.append(x)

def font(sz, bold=False):
    p = '/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if bold else '')
    return ImageFont.truetype(p, sz)

COLS, CW, CH, PAD = 4, 460, 420, 14
rows = (len(items) + COLS - 1) // COLS
W = COLS * CW + PAD * (COLS + 1)
H = 96 + rows * (CH + PAD)
sheet = Image.new('RGB', (W, H), (18, 18, 22))
dr = ImageDraw.Draw(sheet)
dr.text((PAD, 20), 'Конкурс «Зарянка» (2061.su) — иллюстрации к рассказу, 14 работ',
        font=font(28, True), fill=(255, 120, 120))
dr.text((PAD, 58), 'жюри (JURY) и зритель (VIEWER) отмечены;  № slug — автор · голосов',
        font=font(16), fill=(150, 150, 160))

for i, x in enumerate(items):
    cx = PAD + (i % COLS) * (CW + PAD)
    cy = 96 + (i // COLS) * (CH + PAD)
    im = Image.open(os.path.join(SRC, x['file'])).convert('RGB')
    im.thumbnail((CW - 20, CH - 20 - 60))
    sheet.paste(im, (cx + 10 + (CW - 20 - im.width) // 2, cy + 10))
    dr.text((cx + 12, cy + CH - 52), f"{int(x['n'])}. {x['slug']}",
            font=font(16, True), fill=(240, 240, 240))
    dr.text((cx + 12, cy + CH - 30), f"{x['author']}  ·  {VOTES.get(x['slug'],'?')} гол.",
            font=font(14), fill=(180, 200, 220))
    if x['slug'] in AWARD:
        a = AWARD[x['slug']]
        dr.rectangle([cx + 6, cy + 6, cx + CW - 6, cy + CH - 6], outline=(255, 200, 80), width=4)
        dr.text((cx + CW - 150, cy + 12), a, font=font(16, True), fill=(255, 210, 90))

sheet.save(OUT)
print('saved', OUT, sheet.size, 'работ:', len(items))
