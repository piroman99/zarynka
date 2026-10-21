# -*- coding: utf-8 -*-
"""Сверка подстрочника с собранной новеллой: порядок голосов эп-1 (строки 13..67)
должен совпадать с тем, что реально лежит в vn2/content.js (pg.who / pg.vwho).

Проверяет, что SCRIPT_CAST.md не «живёт своей жизнью»: если разметка разойдётся
со сборкой, тут будет видно, на какой странице.
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _story_cast as C            # карта голосов + разбор строк
import _vo_util as U

# 1) ожидаемая последовательность РЕПЛИК из рассказа (строки приёмной 13..67)
rows, bad, unlabelled = C.build()
if bad or unlabelled:
    raise SystemExit('разметка неполная — сначала починить карту')
exp = [who for i, who, tx in rows if 13 <= i <= 67 and who != C.A]

# 2) фактическая — из content.js (длинная реплика разбита на несколько страниц,
# поэтому одинаковые подряд голоса склеиваем: сравниваем СМЕНУ говорящих)
D = U.load_content()
act = []
for nd in D['nodes']:
    if nd.get('id') not in ('starik', 'reception'):
        continue
    for pg in nd['pages']:
        for vo, tx, who in U.segs_of(pg):
            if who != 'narr':
                act.append(who)


def collapse(seq):
    out = []
    for x in seq:
        if not out or out[-1] != x:
            out.append(x)
    return out


# в content.js голоса записаны как 'narr'/'Старик'/'Сергей'/'Екатерина'
NORM = {'narr': C.A, 'Старик': C.S, 'Сергей': C.G, 'Екатерина': C.K}
act = [NORM.get(x, x) for x in act]
exp, act = collapse(exp), collapse(act)
print('смен говорящего: ожидалось %d, в сборке %d' % (len(exp), len(act)))
if exp == act:
    print('ИТОГ: подстрочник и сборка совпадают (голос в голос)')
    sys.exit(0)
n = min(len(exp), len(act))
for k in range(n):
    if exp[k] != act[k]:
        print('первое расхождение на сегменте %d: подстрочник %s, сборка %s'
              % (k + 1, exp[k], act[k]))
        lo = max(0, k - 3)
        for j in range(lo, min(n, k + 4)):
            mark = ' <<<' if j == k else ''
            print('  %3d  подстр %-10s сборка %-10s%s' % (j + 1, exp[j], act[j], mark))
        break
sys.exit(1)
