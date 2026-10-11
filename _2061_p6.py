#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Probe: les pages 6..14 du concours existent-elles dans Wayback ?"""
import os, re, urllib.request, ssl, time
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '.tmp2061')
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
def get(u, tries=3, t=45):
    for k in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t, context=ctx).read()
        except Exception as e:
            last = e; time.sleep(1.5 + 1.5*k)
    return b''
for p in range(6, 15):
    u = 'https://web.archive.org/web/20201024155926id_/http://2061.su/konkursy/zaryanka-illustrations/?page=%d' % p
    b = get(u)
    n = 0
    if b:
        h = b.decode('utf-8', 'replace')
        n = len(re.findall(r'iwork/([a-z0-9_\-]+)/', h))
        if len(b) > 5000:
            open(os.path.join(OUT, 'page_%d.html' % p), 'wb').write(b)
    print('page', p, 'len', len(b), 'iwork-links', n)
