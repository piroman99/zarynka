# -*- coding: utf-8 -*-
"""Убрать одноразовые диагностические скрипты этой сессии."""
import os
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
pats = ['_diag_cr*.py', '_diag_new*.py', '_diag_shot.py', '_diag_roll.py',
        '_diag_end*.py', '_js_parse.py', '_js_balance.py', '_js_pos.py']
for p in pats:
    for f in glob.glob(os.path.join(HERE, p)):
        os.remove(f)
        print('удалён', os.path.basename(f))
for f in glob.glob(os.path.join(HERE, '_sat', 'dbg_*.png')) + \
         glob.glob(os.path.join(HERE, '_sat', 't_*.png')) + \
         glob.glob(os.path.join(HERE, '_sat', 'sz_*.png')) + \
         glob.glob(os.path.join(HERE, '_sat', 'probe_*.png')) + \
         glob.glob(os.path.join(HERE, '_sat', 'mark_title*.???')) + \
         glob.glob(os.path.join(HERE, '_sat', 'tight_title.png')) + \
         glob.glob(os.path.join(HERE, '_sat', 'cr_text_only.png')) + \
         glob.glob(os.path.join(HERE, '_sat', 't_e_*.jpg')):
    os.remove(f)
    print('удалён', os.path.basename(f))
