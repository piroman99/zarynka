# -*- coding: utf-8 -*-
"""Кроп центра кадра перехода: как выглядит лого в темноте (квадрат/круг?)."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(HERE, 'assets', 'review', 'review_115_trans_logo.png')
im = Image.open(src)
w, h = im.size
box = (w // 2 - 130, h // 2 - 130, w // 2 + 130, h // 2 + 130)
im.crop(box).resize((390, 390), Image.LANCZOS).save(
    os.path.join(HERE, 'assets', 'review', 'review_115_trans_logo_crop.png'))
print('готово', im.size, '-> crop 260 -> x1.5')
