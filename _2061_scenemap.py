#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Из works.json -> таблица (карта сцен) + список путей для полной перекачки."""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, '.tmp2061')
w = json.load(open(os.path.join(T, 'works.json'), encoding='utf-8'))
print('всего работ в works.json:', len(w))
# таблица
lines = ['| # | slug | название | автор | голосов | награда |', '|---|---|---|---|---|---|']
paths = []
for i, x in enumerate(sorted(w, key=lambda z: -(z.get('rate') or 0)), 1):
    lines.append(f"| {i} | {x['slug']} | {x['title']} | {x['author']} | {x['rate']} | {x['award'] or ''} |")
    paths.append(f"/konkursy/zaryanka-illustrations/iwork/{x['slug']}/")
open(os.path.join(T, 'scenes.md'), 'w', encoding='utf-8').write('\n'.join(lines))
json.dump(paths, open(os.path.join(T, 'slugs_all.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('записано scenes.md + slugs_all.json (', len(paths), 'путей )')
print('\n'.join(lines[:8]))
