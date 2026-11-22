# -*- coding: utf-8 -*-
import os
p = "out/avm_v3.mp4"   # дубль avm_v3_epic
if os.path.exists(p):
    os.remove(p)
    print("removed", p)
print(sorted(os.listdir("out")))
