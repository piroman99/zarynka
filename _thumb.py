# -*- coding: utf-8 -*-
"""Миниатюра для просмотра: уменьшаем скриншот, чтобы он реально читался глазами."""
import sys, os
from PIL import Image
src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else src.replace('.png', '_sm.jpg')
maxw = int(sys.argv[3]) if len(sys.argv) > 3 else 420
im = Image.open(src).convert('RGB')
k = min(1.0, maxw / im.width)
if k < 1:
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
im.save(out, 'JPEG', quality=82)
print(out, im.size, os.path.getsize(out), 'B')
