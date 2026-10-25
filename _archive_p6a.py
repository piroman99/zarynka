# -*- coding: utf-8 -*-
"""Архивировать вариант A кадра 6 с Марса (Иван выбрал B)."""
import os
import shutil
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REJ = os.path.join(HERE, 'assets', 'rejected', 'p6')
os.makedirs(REJ, exist_ok=True)
pairs = [('prolog_p6_mars_a__gpt-image-2_0.png', 'p6_mars_A_wide_landing.png',
          'общий план: корабль на равнине, крошечный экипаж')]

for src_name, dst_name, why in pairs:
    src = os.path.join(HERE, 'assets', 'gen', src_name)
    dst = os.path.join(REJ, dst_name)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        os.remove(src)
        with open(os.path.join(HERE, 'assets', 'rejected', 'REJECTED.md'), 'a', encoding='utf-8') as f:
            f.write('- `p6/%s` — кадр 6 с Марса, вариант A (%s); выбран B '
                    '_(%s)_\n' % (dst_name, why, datetime.date.today().isoformat()))
        print('архивирован', src_name)
    else:
        print('нет', src)
