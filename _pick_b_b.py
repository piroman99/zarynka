# -*- coding: utf-8 -*-
"""Выбор Ивана 2026-11-04: S1 = B (угол двора), P6 = B (средний план базы).

Что делает:
  1) архивирует отклонённые A-варианты в assets/rejected/{s1wall,p6}/ + REJECTED.md;
  2) ставит мастером p6 вариант B (assets/final/prolog/p6.png);
  3) прогоняет _prolog_finals.py для s1a с WALL_PLATE = вариант B.

Запуск: python3 _pick_b_b.py
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
FIN = os.path.join(HERE, 'assets', 'final', 'prolog')
REJ = os.path.join(HERE, 'assets', 'rejected')
MD = os.path.join(REJ, 'REJECTED.md')

mv = [
    ('s1wall_a__gpt-image-2_0.png', 's1wall/s1_wall_A_frontal_bucket.png'),
    ('p6luna_a__gpt-image-2_0.jpg', 'p6/p6_luna_A_wide_plain.png'),
]
for src, rel in mv:
    s = os.path.join(GEN, src)
    d = os.path.join(REJ, rel)
    os.makedirs(os.path.dirname(d), exist_ok=True)
    if os.path.exists(s):
        shutil.move(s, d)
        print('архив ->', rel)

lines = [
    ('- `s1wall/s1_wall_A_frontal_bucket.png` — кадр s1, стр. 1 (стена, граффити) вариант A: '
     'фрунтально, ведро и тряпка у стены. Иван 2026-11-04: выбран **B** (угол двора, весенние '
     'тени, фигура спиной) _(2026-11-04)_'),
    ('- `p6/p6_luna_A_wide_plain.png` — кадр p6 (лунная станция) вариант A: общий план с '
     'пустой равниной справа. Иван 2026-11-04: выбран **B** (ряд модулей, леса недостроенной '
     'секции, фигура в скафандре) _(2026-11-04)_'),
]
txt = open(MD, encoding='utf-8').read()
add = [ln for ln in lines if ln.split('`')[1] not in txt]
if add:
    if not txt.endswith('\n'):
        txt += '\n'
    txt += '\n'.join(add) + '\n'
    open(MD, 'w', encoding='utf-8').write(txt)
    print('REJECTED.md: +%d строк' % len(add))

# p6 = вариант B
src = os.path.join(GEN, 'p6luna_b__gpt-image-2_0.png')
if not os.path.exists(src):
    raise SystemExit('нет файла %s' % src)
shutil.copy2(src, os.path.join(FIN, 'p6.png'))
print('p6.png <- p6luna_b (%d B)' % os.path.getsize(os.path.join(FIN, 'p6.png')))

# s1a = вариант B (стена, фрунтально/угол двора)
env = dict(os.environ, WALL_PLATE='s1wall_b__gpt-image-2_0.png')
r = subprocess.run([sys.executable, '_prolog_finals.py', 's1wall'], cwd=HERE, env=env,
                   capture_output=True, text=True)
print(r.stdout.strip() or r.stderr[-400:])
