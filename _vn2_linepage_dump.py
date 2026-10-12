# -*- coding: utf-8 -*-
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.join(HERE, 'assets', 'story.txt')
lines = open(STORY, encoding='utf-8').read().split('\n')
L = {i + 1: ln.strip() for i, ln in enumerate(lines)}
SENT = re.compile(r'(?<=[.!?…])\s+(?=[А-ЯA-Z«—])')
SPEAK = {15: 'Старик', 23: 'Сергей', 25: 'Екатерина', 29: 'Сергей', 31: 'Екатерина',
         33: 'Сергей', 37: 'Сергей', 41: 'Сергей', 43: 'Екатерина', 45: 'Сергей',
         47: 'Екатерина', 49: 'Сергей', 51: 'Екатерина', 53: 'Сергей', 57: 'Сергей',
         61: 'Сергей', 63: 'Екатерина', 65: 'Сергей', 67: 'Екатерина'}


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


for n in range(13, 68):
    t = L.get(n)
    if not t or t.startswith('*'):
        continue
    who = SPEAK.get(n, '')
    for i, p in enumerate(pages(t, 2)):
        mark = ''
        if who and p.lstrip().startswith('—'):
            mark = ' <<< ' + who
        print(f'{n:3d}.{i} {p[:88]}{mark}')
