# -*- coding: utf-8 -*-
"""Убрать черновые скрипты/снимки пиксельных проб кадров 9-12 (шумные, результат в _ovl_fit)."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
KILL = ['_ovl_at.py', '_ovl_band.py', '_ovl_chip.py', '_ovl_diffmap.py', '_ovl_gold.py',
        '_ovl_noise.py', '_ovl_pixcheck.py', '_ovl_pixcheck2.py', '_ovl_s5a_check.py',
        '_ovl_strip.py', '_ovl_summary.py', '_ovl_timing.py', '_ovl_where.py',
        '_ovl_where2.py', '_probe_s5b.py', '_s5a_check.py', '_s5a_check2.py',
        '_s5a_redcount.py', '_s5a_stab.py', '_s5ab_panels.py', '_s5a_band_B.py',
        os.path.join('_sat', '_one_s5a_0.png'), os.path.join('_sat', '_one_s5a_1.png'),
        os.path.join('_sat', '_one_s5a_crop.png'), os.path.join('_sat', 's5a_band_mock.png'),
        os.path.join('_sat', 's5a_band_v1.png'), os.path.join('_sat', 's5a_band_B.png')]
gone = 0
for rel in KILL:
    p = os.path.join(HERE, rel)
    if os.path.exists(p):
        os.remove(p)
        gone += 1
        print('удалён', rel)
print('итого удалено:', gone)
