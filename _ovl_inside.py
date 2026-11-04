# -*- coding: utf-8 -*-
"""Пиксельное доказательство: текст титр-слоя лежит ВНУТРИ плашки и по центру.

Для каждой страницы с pg.ovl:
  * плашка и строка берутся из content.js (2400x1350 -> /1.875 = 1280x720),
  * внутри плашки ищем пиксели цвета строки (допуск 40 на канал),
  * печатаем найденный bbox, сравниваем с ожидаемым (по шрифтовым метрикам).
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(HERE, '.tmp_vo')
SCALE = 1280 / 2400.0
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'

src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))
_d = ImageDraw.Draw(Image.new('RGB', (8, 8)))


def hxv(c):
    c = c.lstrip('#')
    return tuple(int(c[k:k + 2], 16) for k in (0, 2, 4))


pages = []
for nd in D['nodes']:
    if nd.get('t') != 'scene':
        continue
    for i, pg in enumerate(nd.get('pages', [])):
        if pg.get('ovl'):
            pages.append((nd['id'], i, pg['ovl']))

bad = 0
for nid, pi, ovl in pages:
    f = os.path.join(TMP, 'ovl_%s_%d.png' % (nid, pi))
    im = Image.open(f).convert('RGB')
    px = im.load()
    box = next(it['b'] for it in ovl if 'b' in it)
    bx0, by0 = int(round(box[0] * SCALE)), int(round(box[1] * SCALE))
    bx1, by1 = int(round(box[2] * SCALE)), int(round(box[3] * SCALE))
    print('\n%s стр.%d  плашка %s..%s (1280)' % (nid, pi + 1, (bx0, by0), (bx1, by1)))
    for it in ovl:
        if 'b' in it:
            continue
        col = hxv(it['c'])
        hits = [(x, y) for y in range(by0 + 3, by1 - 2) for x in range(bx0 + 3, bx1 - 2)
                if all(abs(px[x, y][k] - col[k]) < 26 for k in range(3))]
        font = ImageFont.truetype(LATO_B if it.get('f') == 'l' else GOTHIC, it['s'])
        tw = _d.textlength(it['t'], font=font)
        exp0 = (it['x'] - tw / 2) * SCALE
        exp1 = (it['x'] + tw / 2) * SCALE
        if not hits:
            print('   %-28r НЕТ пикселей цвета текста внутри плашки' % it['t'][:26])
            bad += 1
            continue
        x0 = min(h[0] for h in hits)
        x1 = max(h[0] for h in hits)
        y0 = min(h[1] for h in hits)
        y1 = max(h[1] for h in hits)
        dc = ((x0 + x1) / 2.0) - (exp0 + exp1) / 2.0
        print('   %-28r пикселей %5d  bbox x %d..%d y %d..%d  отличие центра от '
              'расчётного %+.1f px  (плашка центр x %.1f)'
              % (it['t'][:26], len(hits), x0, x1, y0, y1, dc, (bx0 + bx1) / 2.0))
        if abs(dc) > 6:
            bad += 1
print('\nстрок не на месте: %d' % bad)
sys.exit(1 if bad else 0)
