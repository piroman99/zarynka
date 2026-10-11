#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sondage: page du concours d'illustrations «Зарянка» (2061.su) via Wayback.
Telecharge le HTML brut et liste les images / liens de travaux."""
import os, re, json, urllib.request, ssl

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '.tmp2061')
os.makedirs(OUT, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
        return r.read()

SNAP = 'https://web.archive.org/web/20201024155926id_/http://2061.su/konkursy/zaryanka-illustrations/'
html = get(SNAP).decode('utf-8', 'replace')
open(os.path.join(OUT, 'listing.html'), 'w', encoding='utf-8').write(html)
print('html bytes', len(html))

# liens vers les travaux
works = sorted(set(re.findall(r'href="[^"]*?(/konkursy/zaryanka-illustrations/work/[^"?#]+)', html)))
print('works links:', len(works))
# images
imgs = sorted(set(re.findall(r'(?:src|data-src|href)="([^"]+?\.(?:jpg|jpeg|png|webp))"', html, re.I)))
print('imgs:', len(imgs))
for i in imgs[:15]:
    print('  IMG', i)
print('---')
for w in works[:15]:
    print('  W', w)
json.dump({'works': works, 'imgs': imgs}, open(os.path.join(OUT, 'links.json'), 'w'), ensure_ascii=False, indent=1)
