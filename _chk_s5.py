# -*- coding: utf-8 -*-
import os, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
def h(p):
    if not os.path.exists(p): return None
    return hashlib.md5(open(p,'rb').read()).hexdigest()[:12]
for rel in ['assets/final/prolog/s4.png','assets/final/prolog/s5.png','assets/final/prolog/s5_WRONG_tv.png',
            'assets/gen/prologfin6_s5_a_0.jpg','assets/gen/prologfin4_s4_d_0.jpg',
            'vn2/img/prolog/s4.png','vn2/img/prolog/s5.png']:
    p=os.path.join(HERE,rel)
    print(rel, os.path.exists(p), os.path.getsize(p) if os.path.exists(p) else '-', h(p))
