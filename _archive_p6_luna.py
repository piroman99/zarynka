# -*- coding: utf-8 -*-
"""Архив отклонённого по кадру p6 (решение Ивана 2026-11-04) + запись в REJECTED.md.

Иван: «P6 — композит не надо. И не нужна там марсианская охра, это лунная станция.
P6 пересобери как лунную станцию».

Уезжают:
  assets/final/prolog/p6.png            -> assets/rejected/p6/p6_mars_B_mid_dust.png
  assets/gen/p6_base_var{A,B,C}_0.png   -> assets/rejected/p6/composite/
Ничего не удаляем (правило Ивана: кадр только архивируется, с причиной).

Запуск: python3 _archive_p6_luna.py
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
FIN = os.path.join(HERE, 'assets', 'final', 'prolog')
REJ = os.path.join(HERE, 'assets', 'rejected', 'p6')
CMP = os.path.join(REJ, 'composite')
MD = os.path.join(HERE, 'assets', 'rejected', 'REJECTED.md')
os.makedirs(CMP, exist_ok=True)

LINES = [
    ('- `p6/p6_mars_B_mid_dust.png` — кадр 6 в версии «Марс» (средний план: двое в старых '
     'скафандрах идут по красной пыли). Иван 2026-11-04: «это лунная станция, а не Марс; '
     'композит не надо» — вместо Марса база на Луне, генерация `_prolog_p6_luna.py` '
     '_(2026-11-04)_'),
    ('- `p6/composite/p6_base_varA|B|C_0.png` — композитные варианты «лунная база» (вырезанный '
     'силуэт станции из тизера + марсианская охра, `_p6_base.py`). Иван 2026-11-04: '
     '«композит не надо» — база рисуется моделью в кадре, а не вклеивается силуэтом '
     '_(2026-11-04)_'),
]

moved = []
src_fin = os.path.join(FIN, 'p6.png')
dst_fin = os.path.join(REJ, 'p6_mars_B_mid_dust.png')
if os.path.exists(src_fin):
    shutil.move(src_fin, dst_fin)
    moved.append(dst_fin)

for v in ('A', 'B', 'C'):
    src = os.path.join(GEN, 'p6_base_var%s_0.png' % v)
    if os.path.exists(src):
        shutil.move(src, os.path.join(CMP, os.path.basename(src)))
        moved.append(src)

for m in moved:
    print('архив ->', os.path.relpath(m, HERE))

txt = open(MD, encoding='utf-8').read()
add = [ln for ln in LINES if ln.split('`')[1] not in txt]
if add:
    if not txt.endswith('\n'):
        txt += '\n'
    txt += '\n'.join(add) + '\n'
    open(MD, 'w', encoding='utf-8').write(txt)
    print('REJECTED.md: +%d строк' % len(add))
else:
    print('REJECTED.md: записи уже есть')
