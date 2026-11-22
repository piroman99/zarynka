# -*- coding: utf-8 -*-
"""Убрать из клиентской сборки устаревший кадр s2 (узел переименован в p8)."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
IMG = os.path.join(ROOT, "vn2", "img", "prolog")

for old in ("s2.webp", "s2.png", "s2.jpg"):
    p = os.path.join(IMG, old)
    if os.path.exists(p):
        os.remove(p)
        print("удалён", old)
    else:
        print("нет", old)

print("в сборке:", sorted(os.listdir(IMG)))
