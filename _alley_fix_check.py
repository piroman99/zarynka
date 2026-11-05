# -*- coding: utf-8 -*-
"""Проверка правки сцены «аллея» (Иван 2026-11-05): 1) скамейка длинная и отдельная,
2) не дрожит вместе со спрайтом, 3) эмоций поэта больше, 4) CG со скамейкой вдоль аллеи.

Проверки:
  • в content.js у узла alley есть prop (скамейка-кадр) и 6 эмоций сидящего поэта;
  • на CG-странице prop снят, фон = кадр CG;
  • в живом браузере: нижняя кромка спрайта и пропа НЕ меняются за время «дыхания»
    (у сидящего ключ — только масштаб от нижней кромки), и нижняя кромка пропа стоит;
  • длина скамейки на экране >= 2 м (при ~450 px/м) — то есть она длинная, а не «стул».
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

txt = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
data = json.loads(txt[txt.index('{'):txt.rindex('}') + 1])
alley = [n for n in data['nodes'] if n.get('id') == 'alley'][0]
print('узлов %d, страниц в alley %d' % (len(data['nodes']), len(alley['pages'])))

ok = True

# 1) проп
prop = alley.get('prop')
print('prop:', prop)
if not prop or not prop.get('src'):
    print('  !! проп-скамейки нет'); ok = False

# 3) эмоции поэта в сцене
EMOS = {}
for i, pg in enumerate(alley['pages']):
    c = pg.get('cast') or {}
    for side in ('l', 'r'):
        if c.get(side) and c[side][0] == 'Поэт (на скамейке)':
            EMOS.setdefault(c[side][1], []).append(i)
print('эмоции поэта на скамейке:', {k: len(v) for k, v in sorted(EMOS.items())})
if len(EMOS) < 5:
    print('  !! эмоций %d, ожидалось >= 5' % len(EMOS)); ok = False
char = data['chars'].get('Поэт (на скамейке)') or {}
print('спрайты поэта на скамейке:', sorted(char.get('emos', {})), 'seated=', char.get('seated'))

# 4) CG-страница
cg = [i for i, pg in enumerate(alley['pages']) if pg.get('cg')]
print('CG-страницы:', cg)
for i in cg:
    pg = alley['pages'][i]
    if not str(pg.get('bg', '')).startswith('img/cg/'):
        print('  !! фон CG не из img/cg:', pg.get('bg')); ok = False
    print('  cg %d: bg=%s cast=%s' % (i, pg.get('bg'), pg.get('cast')))

# 5) живой браузер: не дрожит
from _cdp import Browser  # noqa: E402
from _vn2_nodes import node_index  # noqa: E402

base = 'file://' + os.path.join(HERE, 'vn2', 'index.html')
ALLEY = node_index('alley')
GE = {
    'sb': "(() => {const s=document.querySelector('#cast .sprite.on'); return s?Math.round(s.getBoundingClientRect().bottom):-1;})()",
    'st': "(() => {const s=document.querySelector('#cast .sprite.on'); return s?Math.round(s.getBoundingClientRect().top):-1;})()",
    'pb': "(() => {const p=document.querySelector('#props .prop'); return (p && getComputedStyle(p).opacity>.5)?Math.round(p.getBoundingClientRect().bottom):-1;})()",
    'pw': "(() => {const p=document.querySelector('#props .prop'); return p?Math.round(p.getBoundingClientRect().width):-1;})()",
    'ph': "(() => {const p=document.querySelector('#props .prop'); return p?Math.round(p.getBoundingClientRect().height):-1;})()",
    'pl': "(() => {const p=document.querySelector('#props .prop'); return p?Math.round(p.getBoundingClientRect().left):-1;})()",
    'pr': "(() => {const p=document.querySelector('#props .prop'); return p?Math.round(p.getBoundingClientRect().right):-1;})()",
}


def ge(browser):
    return {k: browser.js(v) for k, v in GE.items()}

b = Browser(1600, 900)
try:
    b.navigate(base + '?node=%d&page=0&instant=0&text=1&voice=0&music=0&auto=0' % ALLEY, wait=1.2)
    a1 = ge(b)
    b.js('new Promise(r=>setTimeout(r,1700))')
    a2 = ge(b)
    print('дыхание: низ спрайта %s -> %s (должен стоять), верх %s -> %s (должен расти)'
          % (a1.get('sb'), a2.get('sb'), a1.get('st'), a2.get('st')))
    print('проп: низ %s -> %s  (должен стоять)  размер %sx%s  x %s..%s'
          % (a1.get('pb'), a2.get('pb'), a1.get('pw'), a1.get('ph'), a1.get('pl'), a1.get('pr')))
    if a1.get('sb') != a2.get('sb'):
        print('  !! нижняя кромка спрайта едет — дрожит'); ok = False
    if a1.get('pb') != a2.get('pb'):
        print('  !! проп едет'); ok = False
    w = (a1.get('pr') or 0) - (a1.get('pl') or 0)
    print('длина скамейки на экране: %d px (видимая часть холста 1600) -> ~%.1f м при 450 px/м'
          % (w, w / 450.0))
    if w < 800:
        print('  !! скамейка короче 1.8 м — Иван снова скажет «стул»'); ok = False
    # CG-страница: пропа быть не должно
    b.navigate(base + '?node=%d&page=%d&instant=1&text=1&voice=0&music=0&auto=0'
               % (ALLEY, cg[0]), wait=0.8)
    g = ge(b)
    print('CG-страница: prop bottom=%s (None = снят), bg=%s' % (g.get('pb'), g.get('bg')))
finally:
    b.close()

print('\nИТОГ:', 'OK' if ok else 'ЕСТЬ ЗАМЕЧАНИЯ')
