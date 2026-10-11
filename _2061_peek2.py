#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, '.tmp2061', 'iwork_nauchnaia-programma.html')
h = open(p, encoding='utf-8', errors='replace').read()
print('len', len(h))
i = h.find('work__image')
print('idx work__image', i)
if i > 0:
    print(h[i:i+700])
else:
    # montrer la zone de l'image principale
    j = h.find('/media/cache/c6/d6/')
    print('idx img', j)
    print(h[max(0, j-600):j+200])
