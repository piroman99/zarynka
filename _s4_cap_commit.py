# -*- coding: utf-8 -*-
"""Коммит правки S4 (подпись ближе к ТВ) + пуш в origin/rebuild."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))

FILES = [
    '_prolog_finals.py',
    'assets/final/prolog/s4.png',
    'vn2/img/prolog/s4.webp',
    'assets/review/review_113_s4_cap_before.png',
    'assets/review/review_113_s4_cap_wide.png',
    'assets/review/review_113_s4_cap_zoom.png',
    '_s4_cap_geom.py', '_s4_cap_dom.py', '_s4_cap_dom2.py', '_s4_cap_before.py',
    '_s4_cap_shot.py', '_s4_cap_dark.py', '_s4_cap_rows.py', '_s4_cap_full.py',
    '_s4_cap_profile.py', '_s4_cap_ascii.py', '_s4_cap_cream.py', '_s4_cap_measure.py',
    '_s4_cap_measure2.py', '_s4_cap_check.py', '_s4_cap_check2.py', '_s4_text_geom.py',
    '_s4_webp_geom.py', '_s4_geom.py', '_s4_geom2.py', '_s4_geom3.py',
]
MSG = ('VN эп1 (vn2): S4 «видеоролик» — подпись «а что же обычных людей нет?» поднята '
       'к телевизору и уменьшена (кегль 52->42, плашка 862..1535 x 684..762 в 2400x1350): '
       'на наезде камеры 1.0->1.5 она больше не уходит под подстрочник (#box): '
       'низ подписи 61%->70% высоты кадра, зазор до #box 135 px при 1600x900; '
       'в покое строка 34 px, на наезде 50 px. Пересборка 0 ₽ (плашка из кэша), '
       'снимки review_113 (до/покой/наезд), проверки _s4_cap_*.py')


def run(args, **kw):
    print('$', ' '.join(args))
    r = subprocess.run(args, cwd=HERE, text=True, **kw)
    return r


run(['git', 'add'] + FILES, check=True)
run(['git', 'commit', '-m', MSG], check=True)
run(['git', 'push', 'origin', 'HEAD:rebuild'], check=True)
run(['git', 'log', '--oneline', '-1'], check=True)
run(['git', 'status', '--short'], check=False)
