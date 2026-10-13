# -*- coding: utf-8 -*-
import os
HERE = os.path.dirname(os.path.abspath(__file__))
lines = open(os.path.join(HERE, 'assets', 'story.txt'), encoding='utf-8').read().split('\n')
L = {i + 1: ln.strip() for i, ln in enumerate(lines)}
p9 = L[9]
cut = p9.find('Кто-то на скорую руку')
cut2 = p9.find('Через неделю лозунг')
cut3 = p9.find('Любой мог подать заявку')
cut4 = p9.find('Тысячи людей вспомнили')
SEG9 = [p9[:cut], p9[cut:cut2], p9[cut2:cut3], p9[cut3:cut4], p9[cut4:]]
for i, s in enumerate(SEG9):
    print('--- SEG9[%d] (%d зн) ---' % (i, len(s)))
    print(s)
    print()
