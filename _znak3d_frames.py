# -*- coding: utf-8 -*-
"""Одиночные кадры призмы (для визуальной проверки) + ребро крупно."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '_znak3d.py')).read().split("if '--sheet' in sys.argv:")[0]
ns = {'__file__': os.path.join(HERE, '_znak3d.py'), '__name__': 'z3d'}
exec(compile(src, '_znak3d.py', 'exec'), ns)
render, REVIEW = ns['render'], ns['REVIEW']
from PIL import Image
# один угол
render(45).resize((640, 640), Image.LANCZOS).save(os.path.join(REVIEW, 'review_47_znak45.png'))
render(90).crop((380, 300, 900, 980)).save(os.path.join(REVIEW, 'review_48_rib90.png'))
print('ok')
