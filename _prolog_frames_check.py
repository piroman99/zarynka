# -*- coding: utf-8 -*-
"""Проверка кадров-моков: яркость/контраст (не пустые ли)."""
import os
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(HERE, "assets", "mock", "prolog")
for n in ("s1", "s2", "s3", "s4", "s5", "s6"):
    a = np.asarray(Image.open(os.path.join(S, n + ".png")).convert("L"), dtype=np.float32)
    print(f"{n}: mean={a.mean():6.1f} std={a.std():6.1f} min={a.min():3.0f} max={a.max():3.0f} "
          f"dark%={100*(a<25).mean():4.1f}")
