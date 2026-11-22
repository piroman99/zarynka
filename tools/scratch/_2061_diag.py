#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, hashlib
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.tmp2061')
for p in range(1, 6):
    f = os.path.join(OUT, f'page_{p}.html')
    h = open(f, encoding='utf-8', errors='replace').read()
    slugs = sorted(set(re.findall(r'iwork/([a-z0-9_\-]+)', h)))
    thumbs = re.findall(r'/media/cache/[0-9a-f/]+\.jpg', h)
    print(f'page {p}: uniq_slugs={len(slugs)} thumbs={len(thumbs)} md5={hashlib.md5(h.encode()).hexdigest()[:8]}')
    print('   ', slugs[:20])
