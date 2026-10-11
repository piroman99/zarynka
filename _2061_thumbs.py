#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Telecharge les vignettes du concours d'illustrations «Зарянка» (2061.su) via Wayback,
et construit une planche-contact de toutes les oeuvres."""
import os, re, json, time, urllib.request, ssl

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '.tmp2061')
TH = os.path.join(OUT, 'thumbs')
os.makedirs(TH, exist_ok=True)
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}

def get(url, tries=5):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90, context=ctx) as r:
                return r.read()
        except Exception as e:
            time.sleep(2 + 2 * t)
    return b''

items = []   # list of (slug, thumb_rel)
seen = set()
for p in range(1, 16):
    url = f'https://web.archive.org/web/20201024155926id_/http://2061.su/konkursy/zaryanka-illustrations/?page={p}'
    html = get(url).decode('utf-8', 'replace')
    if not html:
        print('page', p, 'EMPTY -> stop'); break
    # parcours sequentiel : lien iwork/<slug> puis vignette /media/cache/...
    toks = re.findall(r'iwork/([a-z0-9_\-]+)|(/media/cache/[0-9a-f/]+\.jpg)', html)
    cur = None; found = 0
    for slug, thumb in toks:
        if slug:
            cur = slug
        elif thumb and cur and cur not in seen:
            items.append((cur, thumb)); seen.add(cur); found += 1
    print(f'page {p}: +{found} (total {len(items)})')
    if found == 0:
        break
    time.sleep(1)

json.dump(items, open(os.path.join(OUT, 'items.json'), 'w'), ensure_ascii=False, indent=1)
print('TOTAL oeuvres:', len(items))

# telechargement des vignettes
ok = 0
for i, (slug, rel) in enumerate(items):
    dst = os.path.join(TH, f'{i:03d}_{slug}.jpg')
    if os.path.exists(dst) and os.path.getsize(dst) > 1000:
        ok += 1; continue
    u = 'https://web.archive.org/web/2020id_/http://2061.su' + rel
    data = get(u, tries=4)
    if data and data[:2] == b'\xff\xd8':
        open(dst, 'wb').write(data); ok += 1
    else:
        print('  FAIL', i, slug, len(data))
    if i % 10 == 0:
        print('  ...', i, ok)
print('downloaded ok:', ok, '/', len(items))
