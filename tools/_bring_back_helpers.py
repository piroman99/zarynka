# -*- coding: utf-8 -*-
"""Вернуть служебные скрипты уборки из workspace/_station_scripts в tools/."""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(os.path.dirname(os.path.dirname(ROOT)), '_station_scripts')

WANT = ['_privacy_sweep.py', '_restore_overzealous.py', '_restore_push.py',
        '_show_stay.py', '_secrets_scan.py', '_verify_after_move.py']
print('в каталоге вынесенных: %d файлов' % len(os.listdir(SRC)))
for name in WANT:
    p = os.path.join(SRC, name)
    dst = os.path.join(HERE, name)
    if os.path.exists(p) and not os.path.exists(dst):
        shutil.move(p, dst)
        print('возвращён', name)
    elif os.path.exists(dst):
        print('уже на месте', name)
    else:
        print('нет', name)
