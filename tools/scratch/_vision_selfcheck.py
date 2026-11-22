# -*- coding: utf-8 -*-
"""Самопроверка зрения: рисуем PNG с кодом, код НЕ печатаем. Скажу его, если увижу файл."""
import os
import random
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
code = ''.join(random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(5))
im = Image.new('RGB', (640, 200), (12, 14, 20))
d = ImageDraw.Draw(im)
d.rectangle([20, 20, 620, 180], outline=(255, 210, 120), width=4)
d.text((40, 90), 'CODE ' + code, fill=(255, 255, 255))
p = os.path.join(ROOT, '_sat', 'vision_check.png')
im.save(p)
open(os.path.join(ROOT, '_sat', 'vision_check_answer.txt'), 'w').write(code)
print('saved', p)
