# -*- coding: utf-8 -*-
from PIL import Image
import glob, os
print("=== source images ===")
for p in sorted(glob.glob("assets/gen/ok_*.jpg")):
    im = Image.open(p)
    print(f"{p:45s} {im.width}x{im.height}  ar={im.width/im.height:.3f}")
print()
print("=== out frames ===")
for p in sorted(glob.glob("out/*.png")):
    im = Image.open(p)
    print(f"{p:45s} {im.width}x{im.height}")
