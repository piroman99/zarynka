# -*- coding: utf-8 -*-
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
for d in ('.tmp_intro3', 'assets/gen/vid'):
    p = os.path.join(HERE, d)
    print('==', d, 'exists' if os.path.exists(p) else 'НЕТ')
    if os.path.isdir(p):
        for f in sorted(os.listdir(p))[:20]:
            fp = os.path.join(p, f)
            print('   %-28s %10d' % (f, os.path.getsize(fp)))
for p in ['assets/gen/logo_a_0.jpg', 'assets/gen/logo_b_0.jpg', 'assets/gen/logo_c_0.jpg',
          'vn2/img/logo.png', 'assets/gen/ok_reception_fix2_0.jpg',
          'assets/gen/ok_x_kate_moon_0.jpg', 'assets/sprites/kate_overalls.png']:
    fp = os.path.join(HERE, p)
    try:
        im = Image.open(fp)
        print('%-40s %s %s %d KB' % (p, im.size, im.mode, os.path.getsize(fp) // 1024))
    except Exception as e:
        print('%-40s ERR %s' % (p, e))
