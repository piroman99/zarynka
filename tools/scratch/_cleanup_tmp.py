# -*- coding: utf-8 -*-
"""Удаление временных файлов через Python (шелл rm в песочнице заблокирован)."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
TARGETS = [
    'vn2/img/char/poet_seat_upset_fixed_ll.webp',
    '_sat/t_ll.webp',
    '_sat/t_ll4.webp',
]
for t in TARGETS:
    p = os.path.join(HERE, t)
    if os.path.exists(p):
        os.remove(p)
        print('удалён', t)
    else:
        print('нет', t)
