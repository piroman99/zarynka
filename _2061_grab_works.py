#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Telecharge toutes les oeuvres du concours d'illustrations «Зарянка» (2061.su) via Wayback.
Pour chaque slug iwork : recupere la page, extrait l'image principale + le titre, telecharge l'image.
Resumable."""
import os, re, json, time, ssl, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '.tmp2061')
FULL = os.path.join(OUT, 'full')
os.makedirs(FULL, exist_ok=True)
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}

def get(u, tries=5, t=60):
    last = b''
    for k in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t, context=ctx).read()
        except Exception as e:
            last = str(e).encode()
            time.sleep(2 + 2 * k)
    return b''

d = json.load(open(os.path.join(OUT, 'slugs.json')))
iw = d['iwork']
slugs = sorted(iw.keys())
meta = {}
mf = os.path.join(OUT, 'meta.json')
if os.path.exists(mf):
    meta = json.load(open(mf))

main_re = re.compile(r'<div imageBlock[^>]*>\s*<a[^>]*>\s*<img[^>]*src="(/media/cache/[0-9a-f/]+\.jpg)"[^>]*alt="([^"]*)"', re.S)
main_re2 = re.compile(r'imageBlock.*?<img[^>]*src="([^"]+\.(?:jpg|jpeg|png))"[^>]*?alt="([^"]*)"', re.S)

done = 0
for n, slug in enumerate(slugs):
    dst = os.path.join(FULL, slug + '.jpg')
    if os.path.exists(dst) and os.path.getsize(dst) > 2000:
        done += 1
        continue
    ts, st = iw[slug]
    url = f'https://web.archive.org/web/{ts}id_/http://2061.su/konkursy/zaryanka-illustrations/iwork/{slug}/'
    h = get(url).decode('utf-8', 'replace')
    if not h:
        print('PAGE FAIL', slug); continue
    m = main_re.search(h) or main_re2.search(h)
    if not m:
        print('NO IMG', slug, len(h)); continue
    rel, alt = m.group(1), m.group(2)
    img = get('https://web.archive.org/web/' + ts + 'id_/http://2061.su' + rel, tries=4)
    if len(img) < 1000:
        # fallback: capture plus large (sans `id_`) 
        img = get('https://web.archive.org/web/' + ts + 'id_/http://2061.su' + rel, tries=4)
    if img[:2] == b'\xff\xd8' or img[:8] == b'\x89PNG\r\n\x1a\n':
        open(dst, 'wb').write(img)
        meta[slug] = {'title': alt, 'img': rel, 'ts': ts, 'bytes': len(img)}
        json.dump(meta, open(mf, 'w'), ensure_ascii=False, indent=1)
        done += 1
    else:
        print('IMG FAIL', slug, len(img), img[:8])
    if n % 10 == 0:
        print(f'  {n}/{len(slugs)} done={done}', flush=True)
    time.sleep(0.4)

print('FINI:', done, '/', len(slugs))
