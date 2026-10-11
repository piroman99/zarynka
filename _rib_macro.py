# -*- coding: utf-8 -*-
"""Крупный план ребра с гравировкой (проверка читаемости)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '_intro_k2b.py')).read().split("if '--sheet' in sys.argv:")[0]
ns = {'__file__': os.path.join(HERE, '_intro_k2b.py'), '__name__': 'k2bmod'}
exec(compile(src, '_intro_k2b.py', 'exec'), ns)
render, REVIEW = ns['render'], ns['REVIEW']
for tt in (2.15, 2.45, 2.85):
    fr = render(int(tt * 25)).crop((700, 0, 1220, 1080))
    out = os.path.join(REVIEW, 'review_37_rib_macro_%.2f.png' % tt)
    fr.save(out)
    print('saved', os.path.relpath(out, HERE), fr.size)
