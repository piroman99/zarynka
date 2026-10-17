# -*- coding: utf-8 -*-
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
for rel in ['assets/final/prolog/s4.png','assets/final/prolog/s5.png',
            'assets/gen/prologfin6_s5_a_0.jpg','assets/gen/prologfin4_s4_d_0.jpg',
            'vn2/img/prolog/s4.png','vn2/img/prolog/s5.png',
            'assets/rejected/s5/s5_WRONG_tv.png']:
    p = os.path.join(HERE, rel)
    if os.path.exists(p):
        im = Image.open(p)
        print(rel, im.size, im.mode, os.path.getsize(p))
    else:
        print(rel, 'MISSING')
