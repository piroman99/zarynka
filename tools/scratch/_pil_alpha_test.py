# -*- coding: utf-8 -*-
"""Проверка: что PIL делает с альфой при PERSPECTIVE (заливает фон или нет)."""
import numpy as np
from PIL import Image

im = Image.new('RGBA', (200, 100), (0, 0, 0, 0))
for x in range(50, 150):
    for y in range(30, 70):
        im.putpixel((x, y), (200, 100, 50, 255))
a = np.asarray(im)
print('исходник: непрозрачных %d из %d' % ((a[:, :, 3] > 0).sum(), a[:, :, 3].size))

coeffs = [1, 0.1, 0, 0.1, 1, 0, 0.0002, 0.0001]
for resample in (Image.NEAREST, Image.BILINEAR, Image.BICUBIC):
    out = im.transform((200, 100), Image.PERSPECTIVE, coeffs, resample)
    b = np.asarray(out)
    print('%s: непрозрачных %d, альфа мин %d макс %d'
          % (resample, (b[:, :, 3] > 0).sum(), b[:, :, 3].min(), b[:, :, 3].max()))

# как выглядит альфа в углу
out = im.transform((200, 100), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
b = np.asarray(out)
print('углы:', b[0, 0], b[0, 199], b[99, 0], b[99, 199])
