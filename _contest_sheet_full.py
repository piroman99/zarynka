#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Полный контрольный лист артов конкурса «Зарянка» (2061.su) — уникальные работы."""
import os, re
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'refs', 'contest_hi')
OUT = os.path.join(HERE, 'assets', 'review', 'review_27_contest_full.png')

AWARD = {'nauchnaia-programma': 'JURY', 'ekaterina-ivanovna-zarianka': 'VIEWER'}

votes, titles, authors = {}, {}, {}
sc = os.path.join(HERE, '.tmp2061', 'scenes.md')
for ln in open(sc, encoding='utf-8'):
    m = re.match(r'\s*\|\s*(\d+)\s*\|\s*(\S+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(\d+)\s*\|', ln)
    if m:
        titles[m.group(2)] = m.group(3)
        authors[m.group(2)] = m.group(4)
        votes[m.group(2)] = int(m.group(5))

# собрать уникальные работы по slug, выбрав самый полный файл
by = {}
for fn in os.listdir(SRC):
    if not fn.lower().endswith('.jpg'):
        continue
    m = re.match(r'(\d+)_(?:work|iwork)_(.+)\.jpg$', fn)
    if not m:
        continue
    slug = m.group(2)
    fp = os.path.join(SRC, fn)
    sz = os.path.getsize(fp)
    if slug not in by or sz > by[slug][2]:
        by[slug] = (int(m.group(1)), fn, sz)
items = [(slug, v[1], v[2]) for slug, v in by.items()]
items.sort(key=lambda t: (-votes.get(t[0], 0), t[0]))

def font(sz, bold=False):
    p = '/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if bold else '')
    return ImageFont.truetype(p, sz)

COLS, CW, CH, PAD = 5, 400, 440, 14
rows = (len(items) + COLS - 1) // COLS
W = COLS * CW + PAD * (COLS + 1)
H = 108 + rows * (CH + PAD)
sheet = Image.new('RGB', (W, H), (18, 18, 22))
dr = ImageDraw.Draw(sheet)
dr.text((PAD, 18), 'Конкурс «Зарянка» (2061.su) — иллюстрации к рассказу Горбова, 2016',
        font=font(30, True), fill=(255, 120, 120))
dr.text((PAD, 60), f'{len(items)} уникальных работ · по голосам зрителей ↓ · '
                   'золотая рамка = победитель жюри / зрителя',
        font=font(17), fill=(160, 160, 172))

for i, (slug, fn, sz) in enumerate(items):
    cx = PAD + (i % COLS) * (CW + PAD)
    cy = 108 + (i // COLS) * (CH + PAD)
    im = Image.open(os.path.join(SRC, fn)).convert('RGB')
    im.thumbnail((CW - 20, CH - 20 - 70))
    sheet.paste(im, (cx + 10 + (CW - 20 - im.width) // 2, cy + 10))
    t = titles.get(slug, slug)
    if len(t) > 34:
        t = t[:33] + '…'
    dr.text((cx + 12, cy + CH - 56), t, font=font(17, True), fill=(240, 240, 240))
    au = (authors.get(slug) or '').strip() or '—'
    dr.text((cx + 12, cy + CH - 32), f"{au}  ·  {votes.get(slug,'?')} гол.",
            font=font(15), fill=(180, 200, 220))
    if slug in AWARD:
        dr.rectangle([cx + 6, cy + 6, cx + CW - 6, cy + CH - 6], outline=(255, 200, 80), width=5)
        dr.text((cx + CW - 150, cy + 12), AWARD[slug], font=font(17, True), fill=(255, 210, 90))

sheet.save(OUT)
print('saved', OUT, sheet.size, 'работ:', len(items))
for s, fn, sz in items:
    print(' ', votes.get(s, '?'), s, fn)
