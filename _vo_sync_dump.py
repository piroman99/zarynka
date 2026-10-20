# -*- coding: utf-8 -*-
"""Дамп страниц приёмной: текст, голос, файл, длительность, символы -> с/симв.
Аномальное отношение = рассинхрон текста и озвучки."""
import os, json, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg',
                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
VD = os.path.join(HERE, 'vn2', 'audio', 'vo')
man = json.load(open(os.path.join(VD, '_voices.json'), encoding='utf-8'))

src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))

CACHE = os.path.join(HERE, '.vo_dur_cache.json')
cache = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}


def dur(p):
    if p in cache:
        return cache[p]
    r = subprocess.run([FF, '-i', p, '-f', 'null', '-'], capture_output=True,
                       text=True)
    d = None
    for ln in r.stderr.splitlines():
        if 'Duration:' in ln:
            t = ln.split('Duration:')[1].split(',')[0].strip()
            h, m, s = t.split(':')
            d = int(h) * 3600 + int(m) * 60 + float(s)
    cache[p] = d
    return d


for nid in (sys.argv[1:] or ['reception']):
    nd = [n for n in D['nodes'] if n.get('id') == nid][0]
    print('=== узел %s, %d страниц' % (nid, len(nd['pages'])))
    prev = None
    for i, pg in enumerate(nd['pages']):
        vo = pg.get('vo')
        txt = pg.get('t') or pg.get('text') or ''
        t = txt if isinstance(txt, str) else json.dumps(txt, ensure_ascii=False)
        d = dur(os.path.join(VD, os.path.basename(vo))) if vo else None
        n = len(t)
        ratio = (d / n) if (d and n) else 0
        flag = ''
        if prev and n and prev > 0 and abs(ratio / prev - 1) > 0.6:
            flag = '  <<< сомнительно'
        prev = ratio if ratio else prev
        print('%2d %-10s %-22s %5s s %4d зн %5.3f с/зн %-12s| %s%s'
              % (i, pg.get('who') or 'narr', os.path.basename(vo or '-'),
                 ('%.1f' % d) if d else '?', n, ratio,
                 man.get(vo, {}).get('voice', '-'), t.replace('\n', ' ')[:60],
                 flag))

json.dump(cache, open(CACHE, 'w', encoding='utf-8'))
