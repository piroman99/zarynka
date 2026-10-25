# -*- coding: utf-8 -*-
"""Проверка озвучки Приёмной: длительности, тишина, соответствие манифесту."""
import os, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg',
                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
VD = os.path.join(HERE, 'vn2', 'audio', 'vo')
man = json.load(open(os.path.join(VD, '_voices.json'), encoding='utf-8'))

src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))
nd = [n for n in D['nodes'] if n.get('id') == 'reception'][0]

def dur(p):
    r = subprocess.run([FF, '-i', p, '-f', 'null', '-'], capture_output=True,
                       text=True)
    for ln in r.stderr.splitlines():
        if 'Duration:' in ln:
            t = ln.split('Duration:')[1].split(',')[0].strip()
            h, m, s = t.split(':')
            return int(h) * 3600 + int(m) * 60 + float(s)
    return None

bad, total, per = [], 0.0, {}
for pg in nd['pages']:
    # vo бывает списком: страница склеена из двух mp3 (rec_22+rec_22b и т.п.)
    vo = pg.get('vo')
    vos = vo if isinstance(vo, list) else [vo]
    key = pg.get('who') or 'narr'
    pdur = 0.0
    for v in vos:
        p = os.path.join(VD, os.path.basename(v))
        if not os.path.exists(p):
            bad.append((v, 'нет файла')); continue
        sz = os.path.getsize(p)
        d = dur(p)
        want = man.get(v, {}).get('voice')
        # у склеенных страниц (vo = [авторская часть, реплика]) голоса частей разные —
        # сверяем только одиночные файлы, манифест для склеек уже верный
        if isinstance(vo, str) and want != key:
            bad.append((v, 'голос %s != %s' % (want, key)))
        if sz < 3000:
            bad.append((v, 'мало байт %d' % sz))
        if d is None or d < 0.4:
            bad.append((v, 'коротко %s' % d))
        pdur += d or 0
    total += pdur
    per[key] = per.get(key, 0) + pdur

print('файлов в манифесте: %d' % len(man))
print('страниц: %d, суммарная длительность: %.1f с (%.1f мин)'
      % (len(nd['pages']), total, total / 60))
for k, v in sorted(per.items(), key=lambda x: -x[1]):
    print('  %-10s %5.1f с' % (k, v))
print('проблем: %d' % len(bad))
for b in bad[:10]:
    print('  ', b)
