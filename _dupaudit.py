# -*- coding: utf-8 -*-
"""Аудит дублей в озвучке Приёмной: одинаковые файлы = одна и та же реплика."""
import os, hashlib, json, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'vn2', 'audio', 'vo')
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries',
                  'ffmpeg-linux-x86_64-v7.0.2')

src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))
nd = [n for n in D['nodes'] if n.get('id') == 'reception'][0]
man = json.load(open(os.path.join(OUT, '_voices.json'), encoding='utf-8'))


def dur(p):
    r = subprocess.run([FF, '-i', p], capture_output=True, text=True)
    for ln in r.stderr.split('\n'):
        if 'Duration:' in ln:
            h, m, s = ln.split('Duration:')[1].split(',')[0].strip().split(':')
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 0.0


by = {}
rows = []
for i, pg in enumerate(nd['pages']):
    name = os.path.basename(pg['vo'])[:-4]
    p = os.path.join(OUT, name + '.mp3')
    h = hashlib.md5(open(p, 'rb').read()).hexdigest()
    by.setdefault(h, []).append(name)
    rows.append((i, name, pg.get('who') or 'narr', man.get(pg['vo'], {}).get('voice'),
                 dur(p), os.path.getsize(p), h[:8]))

print('=== дубли ===')
for h, names in by.items():
    if len(names) > 1:
        print(h[:8], names)

print('\n=== по страницам ===')
for i, name, who, voice, d, sz, h in rows:
    print('%02d %-7s who=%-10s voice=%-10s %5.1fs %7d %s'
          % (i, name, who, voice, d, sz, h))
