# -*- coding: utf-8 -*-
"""Архивировать кадр 6 v1 (проводы на космодроме) — Иван: нужны кадры С МАРСА."""
import os
import shutil
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REJ = os.path.join(HERE, 'assets', 'rejected', 'p6')
os.makedirs(REJ, exist_ok=True)
src = os.path.join(HERE, 'assets', 'gen', 'prolog_p6_firstflight__gpt-image-2_0.png')
dst = os.path.join(REJ, 'p6_v1_cosmodrome_farewell.png')
if os.path.exists(src):
    shutil.copy2(src, dst)
    os.remove(src)
    with open(os.path.join(HERE, 'assets', 'rejected', 'REJECTED.md'), 'a', encoding='utf-8') as f:
        f.write('- `p6/p6_v1_cosmodrome_farewell.png` — хроника первого полёта v1: проводы на '
                'космодроме (ракета на столе). Иван: «Там скорее кадры с Марса нужны» '
                '_(%s)_\n' % datetime.date.today().isoformat())
    print('архивирован p6 v1 (космодром)')
else:
    print('нет', src)
