# -*- coding: utf-8 -*-
"""Замер: сколько бы весил эп1 в WebP/JPEG вместо PNG (предложение по весу трафика)."""
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
        png = os.path.getsize(p)
        im = Image.open(p).convert('RGB')
        best_w = best_j = None
        for q in (88, 92):
            b = io.BytesIO()
            im.save(b, 'WEBP', quality=q, method=6)
            if best_w is None or b.tell() < best_w[0]:
                best_w = (b.tell(), q)
            b2 = io.BytesIO()
            im.save(b2, 'JPEG', quality=88, optimize=True, progressive=True)
            best_j = (b2.tell(), 88)
        rows.append((f, png, best_w[0], best_w[1], best_j[0]))

tp = sum(r[1] for r in rows)
tw = sum(r[2] for r in rows)
tj = sum(r[3 - 1] for r in rows)
print('%-26s %9s %9s %9s' % ('файл', 'png', 'webp', 'jpg88'))
for f, png, w, q, j in rows:
    print('%-26s %8.1fK %8.1fK %8.1fK  (webp q%d)' % (f, png / 1024, w / 1024, j / 1024, q))
print('-' * 62)
print('%-26s %8.1fM %8.1fM %8.1fM' % ('ИТОГО', tp / 1048576, tw / 1048576, tj / 1048576))
print('экономия webp: %.1f×  |  jpeg: %.1f×' % (tp / max(tw, 1), tp / max(tj, 1)))
