#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сравниваем живую страницу (GitHub Pages) с локальной сборкой vn2:
content.js / app.js / style.css — по sha256."""
import hashlib
import os
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://piroman99.github.io/zarynka/vn2/'

for name in ('content.js', 'app.js', 'style.css'):
    local = os.path.join(ROOT, 'vn2', name)
    lb = open(local, 'rb').read()
    lh = hashlib.sha256(lb).hexdigest()[:16]
    try:
        req = urllib.request.Request(BASE + name, headers={'Cache-Control': 'no-cache'})
        rb = urllib.request.urlopen(req, timeout=30).read()
        rh = hashlib.sha256(rb).hexdigest()[:16]
        print('%-12s local %s %7d  live %s %7d  %s'
              % (name, lh, len(lb), rh, len(rb), 'OK' if lh == rh else 'DIFF'))
    except Exception as e:
        print('%-12s local %s  live ERROR %s' % (name, lh, e))
