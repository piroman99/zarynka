#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Collecte complete: oeuvres du concours «Зарянка» (2061.su) via Wayback.
Etapes: parse pages locales -> trouve 'vtoraya liga' -> telecharge vignettes.
"""
import os, re, json, time, ssl, urllib.request
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '.tmp2061')
TH = os.path.join(OUT, 'thumbs')
os.makedirs(TH, exist_ok=True)
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
TS = '20201024155926'


def get(u, tries=5, t=60):
    for k in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t, context=ctx).read()
        except Exception:
            time.sleep(1.5 + 1.5 * k)
    return b''


def wb(path):
    return 'https://web.archive.org/web/%sid_/http://2061.su%s' % (TS, path)


def clean(s):
    s = re.sub(r'<[^>]+>', '', s or '')
    s = s.replace('&quot;', '"').replace('&laquo;', '«').replace('&raquo;', '»')
    s = s.replace('&mdash;', '—').replace('&nbsp;', ' ').replace('&amp;', '&')
    return re.sub(r'\s+', ' ', s).strip()


block_re = re.compile(r'<div class="work">(.*?)\n</div>', re.S)
slug_re = re.compile(r'iwork/([a-z0-9_\-]+)/')
thumb_re = re.compile(r'<img src="(/media/cache/[0-9a-f/]+\.jpg)"')
title_re = re.compile(r'work__title"><a[^>]*>(.*?)</a>')
author_re = re.compile(r'work__author"[^>]*>\s*(.*?)</a>', re.S)
rate_re = re.compile(r'work__digit--rate">\s*(\d+)')
comm_re = re.compile(r'work__digit--comments"\s*>\s*(\d+)')
award_re = re.compile(r'class="award\s*\n?\s*([a-z0-9 ]*?)"')

works = OrderedDict()
for p in range(1, 6):
    f = os.path.join(OUT, 'page_%d.html' % p)
    if not os.path.exists(f):
        continue
    h = open(f, encoding='utf-8', errors='replace').read()
    for m in block_re.finditer(h):
        b = m.group(1)
        sm = slug_re.search(b)
        if not sm:
            continue
        slug = sm.group(1)
        th = thumb_re.search(b)
        tt = title_re.search(b)
        au = author_re.search(b)
        ra = rate_re.search(b)
        co = comm_re.search(b)
        aw = award_re.search(b)
        if slug in works:
            continue
        works[slug] = {
            'slug': slug,
            'thumb': th.group(1) if th else None,
            'title': clean(tt.group(1)) if tt else '',
            'author': clean(au.group(1)) if au else '',
            'rate': int(ra.group(1)) if ra else 0,
            'comments': int(co.group(1)) if co else 0,
            'award': (aw.group(1).strip() if aw else ''),
            'page': p,
        }
print('parsed works:', len(works))

# liens "вторая лига" / autres pages
h1 = open(os.path.join(OUT, 'listing.html'), encoding='utf-8', errors='replace').read()
links = sorted(set(re.findall(r'href="(/konkursy/zaryanka-illustrations/[^"#]*)"', h1)))
print('listing links:')
for l in links:
    print('   ', l)

json.dump(list(works.values()), open(os.path.join(OUT, 'works.json'), 'w'),
          ensure_ascii=False, indent=1)

# telecharger les vignettes
ok = fail = 0
for i, w in enumerate(works.values()):
    if not w['thumb']:
        continue
    dst = os.path.join(TH, '%03d_%s.jpg' % (i, w['slug'][:60]))
    if os.path.exists(dst) and os.path.getsize(dst) > 2000:
        ok += 1
        continue
    b = get(wb(w['thumb']), tries=3)
    if b[:2] == b'\xff\xd8' or b[:8] == b'\x89PNG\r\n\x1a\n':
        open(dst, 'wb').write(b)
        ok += 1
    else:
        fail += 1
        print('  thumb FAIL', w['slug'], len(b))
    time.sleep(0.3)
print('thumbs ok=%d fail=%d total=%d' % (ok, fail, len(works)))
print('files on disk:', len(os.listdir(TH)))
