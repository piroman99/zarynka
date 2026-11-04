# -*- coding: utf-8 -*-
"""Склейка озвучки сцены «аллея у ворот» в один mp3 — для прослушки Иваном.

Порядок = порядок страниц в игре (steps, затем alley), между страницами 0.35 с,
между сценами 0.8 с. Пишет out/alley_vo_full.mp3 и печатает тайминги по говорящим.
"""
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg',
                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
VN2 = os.path.join(HERE, 'vn2')
OUT = os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True)

src = open(os.path.join(VN2, 'content.js'), encoding='utf-8').read()
D = json.loads(re.search(r'=\s*(\{.*\})', src, re.S).group(1))

tmp = os.path.join(OUT, '_alley_parts')
os.makedirs(tmp, exist_ok=True)


def sil(sec, name):
    p = os.path.join(tmp, name + '.mp3')
    subprocess.run([FF, '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                    '-t', str(sec), '-b:a', '96k', p], capture_output=True)
    return p


gap = sil(0.35, 'gap')
scene_gap = sil(0.8, 'scene_gap')

parts = []
who_chars = {}
total = 0.0
for nd in D['nodes']:
    if nd.get('id') not in ('steps', 'alley'):
        continue
    if parts:
        parts.append(scene_gap)
    for pg in nd['pages']:
        vo = pg.get('vo')
        if not vo:
            continue
        vos = [vo] if isinstance(vo, str) else list(vo)
        vwho = pg.get('vwho') or [pg.get('who') or 'narr'] * len(vos)
        for i, v in enumerate(vos):
            p = os.path.join(VN2, v)
            if not os.path.exists(p):
                continue
            parts.append(p)
            k = vwho[i]
            who_chars[k] = who_chars.get(k, 0) + len(pg.get('tx') or '')
            parts.append(gap)

lst = os.path.join(tmp, '_list.txt')
with open(lst, 'w', encoding='utf-8') as f:
    for p in parts:
        f.write("file '%s'\n" % p)
dst = os.path.join(OUT, 'alley_vo_full.mp3')
r = subprocess.run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', lst,
                    '-b:a', '96k', dst], capture_output=True, text=True)
if r.returncode != 0:
    raise SystemExit('ffmpeg: ' + r.stderr[-300:])

d = subprocess.run([FF, '-hide_banner', '-i', dst], capture_output=True, text=True).stderr
m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', d)
dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0
print('out/alley_vo_full.mp3  %.1f с  %.0f KB  файлов %d'
      % (dur, os.path.getsize(dst) / 1024, len([p for p in parts if not p.startswith(tmp)])))
print('по говорящим (знаков):', who_chars)
for f in os.listdir(tmp):
    os.remove(os.path.join(tmp, f))
os.rmdir(tmp)
