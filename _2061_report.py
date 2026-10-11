#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rapport: etat de la collecte du concours d'illustrations «Зарянка» (2061.su)."""
import os, re, json
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '.tmp2061')

full = os.path.join(OUT, 'full')
thumbs = os.path.join(OUT, 'thumbs')
print('full/', len(os.listdir(full)) if os.path.isdir(full) else 'no dir',
      'files')
print('thumbs/', len(os.listdir(thumbs)) if os.path.isdir(thumbs) else 'no dir',
      'files')

d = json.load(open(os.path.join(OUT, 'slugs.json')))
iw = d['iwork']
print('iwork slugs:', len(iw))
w = json.load(open(os.path.join(OUT, 'works.json')))
print('works parsed:', len(w))
print('awards:', dict(Counter((x['award'] or '(none)') for x in w)))
print('--- awarded ---')
for x in w:
    if x['award']:
        print('  [%s] %s | %s | %s' % (x['award'], x['title'], x['author'], x['slug']))
print('--- pages present ---')
for p in range(1, 16):
    f = os.path.join(OUT, 'page_%d.html' % p)
    print('  page', p, os.path.getsize(f) if os.path.exists(f) else '-')

# contexte: texte de la page listing
p = os.path.join(OUT, 'listing.html')
if os.path.exists(p):
    h = open(p, encoding='utf-8', errors='replace').read()
    t = re.sub(r'<script.*?</script>', '', h, flags=re.S)
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    print('--- listing text ---')
    print(t[:3000])
