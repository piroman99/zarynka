# -*- coding: utf-8 -*-
"""Архив отвергнутых кадров «Зарянки»: складываем сюда отклонённые варианты,
чтобы не пропадали (с подписью причины). Ничего не удаляем — только переносим.
"""
import os, shutil, json, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
REJ = os.path.join(HERE, 'assets', 'rejected')
os.makedirs(REJ, exist_ok=True)

# (файл-источник, куда положить, причина отклонения)
ITEMS = [
    ('assets/gen/prologfin_s5_0.jpg',   's5/s5_plate_v1_old.jpg',  'старый мок/первый финал S5, забракован'),
    ('assets/gen/prologfin5_s5_a_0.jpg','s5/s5_A_vdnkh.jpg',       'S5 A: вышел ВДНХ (павильон с колоннадой + ракета), не Верховный Совет'),
    ('assets/gen/prologfin5_s5_b_0.jpg','s5/s5_B_vdnkh.jpg',       'S5 B: то же — плакатная тумба + ракета вдали, читается как ВДНХ'),
]

moved = []
for src, dst, why in ITEMS:
    s = os.path.join(HERE, src)
    if not os.path.exists(s):
        print('нет источника:', src)
        continue
    d = os.path.join(REJ, dst)
    os.makedirs(os.path.dirname(d), exist_ok=True)
    shutil.copy2(s, d)
    os.remove(s)
    moved.append({'file': dst, 'reason': why, 'archived': datetime.date.today().isoformat()})
    print('архивирован:', dst)

# журнал причин
log = os.path.join(REJ, 'REJECTED.md')
with open(log, 'a', encoding='utf-8') as f:
    for m in moved:
        f.write('- `%s` — %s _(%s)_\n' % (m['file'], m['reason'], m['archived']))
print('готово, перенесено:', len(moved))
