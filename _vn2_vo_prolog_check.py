# -*- coding: utf-8 -*-
"""Проверка озвучки ВСЕГО пролога (s1, p6, s2..s7): файлы на месте, длительности."""
import os
import json
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg',
                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
VD = os.path.join(HERE, 'vn2', 'audio', 'vo')
PROLOG = ['s1', 'p6', 's2', 's3', 's4', 's5', 's6', 's7']

src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))
nodes = {n.get('id'): n for n in D['nodes'] if n.get('t') == 'scene'}


def dur(p):
    r = subprocess.run([FF, '-i', p, '-f', 'null', '-'], capture_output=True, text=True)
    for ln in r.stderr.splitlines():
        if 'Duration:' in ln:
            t = ln.split('Duration:')[1].split(',')[0].strip()
            h, m, s = t.split(':')
            return int(h) * 3600 + int(m) * 60 + float(s)
    return None


total = 0.0
bad = []
for nid in PROLOG:
    nd = nodes.get(nid)
    if not nd:
        bad.append((nid, 'нет узла'))
        continue
    parts = []
    for pg in nd['pages']:
        p = os.path.join(VD, os.path.basename(pg['vo']))
        if not os.path.exists(p):
            bad.append((pg['vo'], 'нет файла'))
            continue
        d = dur(p) or 0
        total += d
        parts.append('%.1f' % d)
    print('%-4s страниц %d, длительности %s' % (nid, len(nd['pages']), ' '.join(parts)))
print('суммарно пролог: %.1f с' % total)
print('проблем: %d' % len(bad))
for b in bad:
    print('  ', b)
