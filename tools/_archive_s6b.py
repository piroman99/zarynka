# -*- coding: utf-8 -*-
"""Архивировать оставшийся промежуточный S6 (весна, средний план, но без пары из БЛ)."""
import os
import shutil
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
REJ = os.path.join(ROOT, 'assets', 'rejected', 's6')
src = os.path.join(ROOT, 'assets', 'gen', 's6_gpt2_b_0.png')
dst = os.path.join(REJ, 's6_gpt2_B_spring_nocouple.png')
if os.path.exists(src):
    shutil.copy2(src, dst)
    os.remove(src)
    with open(os.path.join(ROOT, 'assets', 'rejected', 'REJECTED.md'), 'a', encoding='utf-8') as f:
        f.write('- `s6/s6_gpt2_B_spring_nocouple.png` — весна, средний план, но без пары Женя+Семён '
                '_(%s)_\n' % datetime.date.today().isoformat())
    print('архивирован s6_gpt2_b_0.png')
else:
    print('нет', src)
