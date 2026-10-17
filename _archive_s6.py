# -*- coding: utf-8 -*-
"""Архивировать отклонённые плашки S6 (зима/толпа/прочие варианты) — не удаляем, см. REJECTED.md."""
import os
import shutil
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REJ = os.path.join(HERE, 'assets', 'rejected', 's6')
os.makedirs(REJ, exist_ok=True)

# (файл в assets/gen, имя в архиве, причина)
ITEMS = [
    ('prologfin7_s6_a_0.jpg', 's6_A_flux2_winter_crowd.jpg',
     'S6 A (flux-2): зима со снегом — в тексте «яркое весеннее солнце»'),
    ('s6_gpt_a_0.png', 's6_gpt_A_winter_hugecrowd.png',
     'gpt-image-2 A: зима + слишком большая очередь'),
    ('s6_gpt_b_0.png', 's6_gpt_B_winter_hugecrowd.png',
     'gpt-image-2 B: зима + слишком большая очередь'),
    ('s6_gpt2_a_0.png', 's6_gpt2_A_spring_wide.png',
     'весна, широкий план — выбран средний план B'),
    ('s6_gpt3_a_0.png', 's6_gpt3_A_couple_midqueue.png',
     'пара в середине очереди, выбран B (пара ближе к камере)'),
]

stamp = datetime.date.today().isoformat()
lines = []
for src_name, dst_name, why in ITEMS:
    src = os.path.join(HERE, 'assets', 'gen', src_name)
    if not os.path.exists(src):
        print('нет', src_name)
        continue
    shutil.copy2(src, os.path.join(REJ, dst_name))
    os.remove(src)
    lines.append('- `s6/%s` — %s _(%s)_' % (dst_name, why, stamp))
    print('архивирован', src_name, '->', dst_name)

if lines:
    with open(os.path.join(HERE, 'assets', 'rejected', 'REJECTED.md'), 'a', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('REJECTED.md дополнен')
