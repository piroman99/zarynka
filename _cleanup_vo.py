# -*- coding: utf-8 -*-
import os, shutil, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
tmp = os.path.join(HERE, '.tmp_vo')
if os.path.isdir(tmp):
    shutil.rmtree(tmp)
    print('removed .tmp_vo')
import pv
print('balance:', json.dumps(pv.balance(), ensure_ascii=False))
