# -*- coding: utf-8 -*-
"""Бюджет озвучки новой сцены «аллея»: символы по говорящим + оценка в рублях.

Цены: gemini-3.8-flash-tts 1.70 ₽ / 1000 зн., elevenlabs-v4-tts 10.84 ₽ / 1000 зн.
Считаем по плану `vof` (файлы, которых ещё нет) — чтобы Иван видел цену до записи.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PRICE = {'gemini': 1.70, 'eleven': 10.84}
VOICE = {'narr': ('закадр', 'gemini', 'Charon'),
         'Екатерина': ('Екатерина', 'eleven', 'Charlotte'),
         'Поэт': ('Поэт', 'gemini', 'НЕ ВЫБРАН')}

src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(re.search(r'=\s*(\{.*\})', src, re.S).group(1))

tot = {}
missing = 0
for nd in D['nodes']:
    if nd.get('id') not in ('steps', 'alley'):
        continue
    for pg in nd['pages']:
        vos = pg.get('vof')
        if not vos:
            continue
        vos = [vos] if isinstance(vos, str) else vos
        vtx = pg.get('vtx') or [pg['tx']] * len(vos)
        vwho = pg.get('vwho') or [pg.get('who') or 'narr'] * len(vos)
        have = pg.get('vo') or []
        have = [have] if isinstance(have, str) else have
        for i, v in enumerate(vos):
            if v in have:
                continue
            missing += 1
            k = vwho[i]
            t = re.sub(r'^[\u2014\u2013-]+\s*', '', vtx[i].strip())
            t = re.sub(r'[,;:]+$', '', t)
            d = tot.setdefault(k, {'chars': 0, 'files': 0})
            d['chars'] += len(t)
            d['files'] += 1

print('файлов к записи: %d' % missing)
total = 0.0
for k, d in sorted(tot.items(), key=lambda x: -x[1]['chars']):
    name, fam, voice = VOICE.get(k, (k, 'gemini', '?'))
    rub = d['chars'] / 1000.0 * PRICE[fam]
    total += rub
    print('  %-11s %-8s %-16s %4d зн.  %2d файл(ов)  ~%5.2f ₽'
          % (name, fam, voice, d['chars'], d['files'], rub))
print('ИТОГО ~ %.2f ₽ (без выбора голоса поэта; если поэт на elevenlabs — дороже)'
      % total)
