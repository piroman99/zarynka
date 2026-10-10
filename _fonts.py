# -*- coding: utf-8 -*-
import os, glob
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
print("bg  ", Image.open(os.path.join(HERE, "assets/gen/bg_reception_vn_0.png")).size)
print("spr ", Image.open(os.path.join(HERE, "assets/sprites/kate_overalls.png")).size)
print("\norig assets:", sorted(os.listdir(os.path.join(HERE, "assets/orig"))))

cands = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
         HERE + "/assets/orig/burlak.ttf"]
for c in cands:
    print(("OK  " if os.path.exists(c) else "--  ") + c)
print("\nall ttf under /usr/share/fonts:",
      len(glob.glob("/usr/share/fonts/**/*.ttf", recursive=True)))
for p in glob.glob("/usr/share/fonts/**/*.ttf", recursive=True)[:12]:
    print("   ", p)
