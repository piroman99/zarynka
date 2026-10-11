#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Диагностика/перекачка: тянем один арт конкурса целиком, сверяем размер и EOI."""
import os, re, subprocess, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://2061.su'
OUT = os.path.join(HERE, '.tmp2061', 'refetch')
os.makedirs(OUT, exist_ok=True)

def get(url, extra=None):
    cmd = ['curl', '-skL', '-m', '120', '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
           '-e', BASE + '/', url]
    if extra:
        cmd[1:1] = extra
    p = subprocess.run(cmd, capture_output=True)
    return p.returncode, p.stdout, p.stderr[:200]

# страница работы
page = BASE + '/konkursy/zaryanka-illustrations/iwork/baba-katia/'
rc, html, err = get(page)
print('page rc', rc, 'len', len(html), err)
html = html.decode('utf-8', 'replace')
# ищем основную картинку (align="middle")
imgs = re.findall(r'src="(/media/cache/[^"]+\.(?:jpg|jpeg|png))"', html)
print('img candidates:', imgs[:6])
if imgs:
    u = BASE + imgs[0]
    rc, data, err = get(u)
    print('img rc', rc, 'len', len(data), 'EOI', data.endswith(b'\xff\xd9'), err)
    fn = os.path.join(OUT, 'test' + os.path.splitext(imgs[0])[1])
    open(fn, 'wb').write(data)
    print('saved', fn, len(data), 'B', hashlib.md5(data).hexdigest()[:10])
