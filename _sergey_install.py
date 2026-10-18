# -*- coding: utf-8 -*-
"""Поставить выбранные варианты (gpt-image-2 v2) в сборку, старые — в rejected."""
import os, shutil, json

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
V2 = os.path.join(GEN, '_sergey_v2')
REJ = os.path.join(HERE, 'assets', 'rejected', 'sergey_emo')
os.makedirs(REJ, exist_ok=True)

PAIRS = [('sergey_smile', 'sergey_smile__gpt-image-2_0.png'),
         ('sergey_concerned', 'sergey_concerned__gpt-image-2_0.png')]

for name, src in PAIRS:
    s = os.path.join(V2, src)
    assert os.path.exists(s), s
    # старый вариант -> rejected
    for old in (os.path.join(GEN, name + '_0.jpg'), os.path.join(GEN, name + '_0.png')):
        if os.path.exists(old):
            dst = os.path.join(REJ, os.path.basename(old))
            shutil.copy2(old, dst)
            os.remove(old)
            print('rejected <-', os.path.basename(old))
    dst = os.path.join(GEN, name + '_0.png')
    shutil.copy2(s, dst)
    print('installed ->', os.path.basename(dst))
