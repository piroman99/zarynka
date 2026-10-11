# -*- coding: utf-8 -*-
import os
HERE = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(HERE, 'assets', 'mock', 'prolog')
for n in ('s1', 's2', 's3', 's4', 's5', 's6'):
    p = os.path.join(M, n + '.png')
    if os.path.exists(p):
        os.remove(p); print('removed', n + '.png')
print(sorted(os.listdir(M)))
