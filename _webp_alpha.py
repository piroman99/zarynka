# -*- coding: utf-8 -*-
"""Оценка WebP С ПРОЗРАЧНОСТЬЮ (спрайты RGBA) и без (кадры) — честно, с сохранением alpha."""
import os, io
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VN = os.path.join(HERE, 'vn2')
rows = []
for sub in ['img/prolog', 'img/char', 'img/bg']:
    d = os.path.join(VN, sub)
    if not os.path.isdir(d):
        continue
    for f in sorted(os.listdir(d)):
        p = os.path.join(d, f)
        im = Image.open(p)
        png = os.path.getsize(p)
        res = []
        for q in (88, 92):
            b = io.BytesIO()
            im.save(b, 'WEBP', quality=q, method=6, lossless=False)
            res.append((q, b.tell()))
        rows.append((sub, f, im.mode, im.size, png, res))

print('%-9s %-14s %-5s %-11s %9s %9s %9s' % ('папка', 'файл', 'mode', 'размер', 'png', 'webp88', 'webp92'))
tp = tw88 = tw92 = 0
for sub, f, mode, size, png, res in rows:
    print('%-9s %-14s %-5s %-11s %8.1fK %8.1fK %8.1fK'
          % (sub.split('/')[-1], f, mode, '%dx%d' % size, png / 1024, res[0][1] / 1024, res[1][1] / 1024))
    tp += png; tw88 += res[0][1]; tw92 += res[1][1]
print('-' * 72)
print('ИТОГО  png %.1f MB | webp q88 %.2f MB | webp q92 %.2f MB' % (tp / 1048576, tw88 / 1048576, tw92 / 1048576))
print('выигрыш: q88 %.1f×, q92 %.1f×' % (tp / tw88, tp / tw92))
