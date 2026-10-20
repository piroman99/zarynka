# -*- coding: utf-8 -*-
"""Показываем, какие сегменты короткие и какие склеятся с авторской вставкой."""
import importlib.util
import re
import sys

HERE = '/home/ivan/.nanobot/workspace/novella/zaryanka'
STORY = HERE + '/assets/story.txt'

lines = open(STORY, encoding='utf-8').read().split('\n')
L = {i + 1: ln.strip() for i, ln in enumerate(lines)}
par = {n: L[n] for n in range(13, 68) if L.get(n) and not L[n].startswith('*')}

SENT = re.compile(r'(?<=[.!?…])\s+(?=[А-ЯA-Z«—])')


def segments(p):
    starts = []
    for m in re.finditer(r'—\s', p):
        i = m.start()
        if i == 0:
            starts.append((i, m.end()))
            continue
        prev = p[:i].rstrip()
        if prev and prev[-1] in ',.?!…:;':
            starts.append((i, m.end()))
    if not starts:
        return [('narr', p.strip())]
    out = []
    if starts[0][0] > 0:
        head = p[:starts[0][0]].strip()
        if head:
            out.append(('narr', head))
    for k, (i, end) in enumerate(starts):
        stop = starts[k + 1][0] if k + 1 < len(starts) else len(p)
        seg = p[end:stop].strip()
        if seg:
            out.append(('speech' if k % 2 == 0 else 'narr', seg))
    return out


for n in sorted(par):
    segs = segments(par[n])
    if len(segs) < 2:
        continue
    print('\n--- абзац %d' % n)
    for k, (kind, tx) in enumerate(segs):
        print('  %d %-6s %3d зн. | %s' % (k, kind, len(tx), tx[:80]))
