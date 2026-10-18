# -*- coding: utf-8 -*-
"""Кто на какой странице по ПАРАГРАФАМ: проверка, что продолжение прямой речи
не уезжает в закадр (там сейчас теряется голос Кати/Сергея)."""
import os, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.join(HERE, 'assets', 'story.txt')
lines = open(STORY, encoding='utf-8').read().split('\n')
L = {i + 1: ln.strip() for i, ln in enumerate(lines)}
SENT = re.compile(r'(?<=[.!?…])\s+(?=[А-ЯA-Z«—])')


def pages(text, maxn=2):
    parts = [s.strip() for s in SENT.split(text) if s.strip()]
    out, cur = [], []
    for s in parts:
        cur.append(s)
        if len(cur) >= maxn:
            out.append(' '.join(cur)); cur = []
    if cur:
        out.append(' '.join(cur))
    return out


src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))
nd = [n for n in D['nodes'] if n.get('id') == 'reception'][0]

i = 0
for n in sorted(k for k in L if 13 <= k <= 67 and L[k] and not L[k].startswith('*')):
    ps = pages(L[n], 2)
    mark = 'SPEECH' if L[n].startswith('—') else 'narr  '
    print('L%-3d %s pages=%d' % (n, mark, len(ps)))
    for j, p in enumerate(ps):
        cur = nd['pages'][i].get('who', '-')
        print('   p%-2d who=%-10s | %s' % (i, cur, p[:70]))
        i += 1
print('всего страниц', i)
