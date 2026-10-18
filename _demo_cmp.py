# -*- coding: utf-8 -*-
"""Сравнить опубликованный content.js с локальным (что видит Иван в демо)."""
import os, json, urllib.request

URL = 'https://piroman99.github.io/zarynka/vn2/content.js'
req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
txt = urllib.request.urlopen(req, timeout=30).read().decode('utf-8')
D = json.loads(txt[txt.index('=') + 1:].strip().rstrip(';'))
print('chars:', list(D['chars']))
rec = [n for n in D['nodes'] if n.get('id') == 'reception']
if not rec:
    print('нет узла reception')
else:
    pgs = rec[0]['pages']
    print('страниц:', len(pgs))
    whos = {}
    for p in pgs:
        whos[p.get('who', '-')] = whos.get(p.get('who', '-'), 0) + 1
    print('who:', whos)
    print('vo sample:', [p.get('vo') for p in pgs[:3]])
    print('cast p0:', pgs[0].get('cast'))
