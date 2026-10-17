# -*- coding: utf-8 -*-
"""Архивировать отклонённый S5 B («Триумф» снизу) — не пропал для истории."""
import os, shutil, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
REJ = os.path.join(HERE, 'assets', 'rejected', 's5')
os.makedirs(REJ, exist_ok=True)
src = os.path.join(HERE, 'assets', 'gen', 'prologfin6_s5_b_0.jpg')
dst = os.path.join(REJ, 's5_B_triumph_lowangle.jpg')
if os.path.exists(src):
    shutil.copy2(src, dst)
    os.remove(src)
    with open(os.path.join(HERE, 'assets', 'rejected', 'REJECTED.md'), 'a', encoding='utf-8') as f:
        f.write('- `s5/s5_B_triumph_lowangle.jpg` — S5 B: ракурс снизу, выбран A _(%s)_\n' % datetime.date.today().isoformat())
    print('архивирован S5 B')
else:
    print('нет', src)
