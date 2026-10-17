# -*- coding: utf-8 -*-
"""Вернуть ПРАВИЛЬНУЮ S5 (Верховный Совет «ТРИУМФ») в финал + пересобрать vn2. 0 руб."""
import os, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'assets', 'gen', 'prologfin6_s5_a_0.jpg')
DST = os.path.join(HERE, 'assets', 'final', 'prolog', 's5.png')
ALT_OLD = os.path.join(HERE, 'assets', 'final', 'prolog', 's5_WRONG_tv.png')

print('SRC exists:', os.path.exists(SRC), 'SRC size:', os.path.getsize(SRC) if os.path.exists(SRC) else None)
print('DST exists:', os.path.exists(DST), 'DST size:', os.path.getsize(DST) if os.path.exists(DST) else None)

# 1) сохранить неправильный (S4/телевизор) на всякий случай
if os.path.exists(DST):
    shutil.copy2(DST, ALT_OLD)
    print('backup wrong s5.png ->', os.path.relpath(ALT_OLD, HERE))

# 2) вернуть правильный
shutil.copy2(SRC, DST)
print('restored s5.png <-', os.path.relpath(SRC, HERE), os.path.getsize(DST), 'B')
