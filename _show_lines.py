# -*- coding: utf-8 -*-
import os
HERE = os.path.dirname(os.path.abspath(__file__))
lines = open(os.path.join(HERE, 'assets', 'story.txt'), encoding='utf-8').read().split('\n')
for n in (25, 29, 33, 37, 47, 53, 57, 63):
    print('L%d: %s' % (n, lines[n - 1].strip()))
    print()
