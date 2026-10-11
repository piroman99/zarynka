# -*- coding: utf-8 -*-
"""Заменить старые пробы S2 (с ракетой) на исправленные (без ракеты)."""
import os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(HERE, 'assets', 'gen')
for base in ('prolog_s2_cin_0', 'prolog_s2_anime_0'):
    old = os.path.join(G, base + '.jpg')
    new = os.path.join(G, base + '_0.jpg')
    if os.path.exists(old):
        os.remove(old)
    if os.path.exists(new):
        shutil.move(new, old)
        print('replaced', base, '->', os.path.getsize(old))
print(sorted(f for f in os.listdir(G) if f.startswith('prolog_s')))
