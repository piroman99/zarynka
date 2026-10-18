# -*- coding: utf-8 -*-
"""Смета озвучки приёмной по голосам: сколько знаков у рассказчика, Сергея, Старика, Кати."""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('window.VN =') + len('window.VN ='):].rstrip().rstrip(';'))
rec = [n for n in D['nodes'] if n.get('id') == 'reception'][0]

by = {}
for pg in rec['pages']:
    who = pg.get('who') or 'рассказчик'
    by.setdefault(who, [0, 0])
    by[who][0] += 1
    by[who][1] += len(pg['tx'])
tot = 0
for who, (n, ch) in sorted(by.items(), key=lambda kv: -kv[1][1]):
    print('%-12s стр=%-3d знаков=%-5d ~%.2f ₽' % (who, n, ch, ch * 1.70 / 1000))
    tot += ch
print('ИТОГО знаков=%d, ~%.2f ₽ (gemini-3.8-flash-tts 1.70/1000)' % (tot, tot * 1.70 / 1000))
print('страниц всего', len(rec['pages']))
