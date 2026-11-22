# -*- coding: utf-8 -*-
"""Подготовка к коммиту «аллея»: спрайт на место, проп скамейки в assets, чистка дубля."""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
CHAR = os.path.join(ROOT, 'vn2', 'img', 'char')
SRC_FIXED = os.path.join(CHAR, 'poet_seat_upset_fixed.webp')
DST_MAIN = os.path.join(CHAR, 'poet_seat_upset.webp')
PROP_SRC = os.path.join(ROOT, '_sat', 'wc', 'prop_B.png')
PROP_DST = os.path.join(ROOT, 'assets', 'sprites', 'prop_bench_blender.png')

# 1) исправленный спрайт — на место рабочего (история в git сохранит прежний)
shutil.copyfile(SRC_FIXED, DST_MAIN)
os.remove(SRC_FIXED)
print('спрайт заменён: %d B' % os.path.getsize(DST_MAIN))

# 2) принятый проп скамейки в исходники
shutil.copyfile(PROP_SRC, PROP_DST)
print('проп: %s %d B' % (os.path.relpath(PROP_DST, HERE), os.path.getsize(PROP_DST)))
