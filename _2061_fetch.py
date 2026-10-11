#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etape 1: recuperer (resumable) les pages HTML du concours d'illustrations «Зарянка»."""
import os, re, json, time, urllib.request, ssl

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '.tmp2061')
os.makedirs(OUT, exist_ok=True)
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}

def get(url, tries=8):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
                return r.read()
        except Exception as e:
            time.sleep(1.5 + 1.5 * t)
    return b''

for p in range(1, 16):
    f = os.path.join(OUT, f'page_{p}.html')
    if os.path.exists(f) and os.path.getsize(f) > 5000:
        print('page', p, 'cached', os.path.getsize(f)); continue
    html = get(f'https://web.archive.org/web/20201024155926id_/http://2061.su/konkursy/zaryanka-illustrations/?page={p}')
    if html and len(html) > 5000:
        open(f, 'wb').write(html); print('page', p, 'OK', len(html))
    else:
        print('page', p, 'FAILED len', len(html))
