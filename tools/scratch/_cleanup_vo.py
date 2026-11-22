# -*- coding: utf-8 -*-
import os, shutil, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
tmp = os.path.join(HERE, '.tmp_vo')
if os.path.isdir(tmp):
    shutil.rmtree(tmp)
    print('removed .tmp_vo')
import pv
print('balance:', json.dumps(pv.balance(), ensure_ascii=False))
