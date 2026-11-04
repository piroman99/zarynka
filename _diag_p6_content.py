# -*- coding: utf-8 -*-
"""Состояние кадра p6 в собранном content.js + озвучка."""
import os, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(HERE, "vn2", "content.js"), encoding="utf-8").read()
i = s.find('"p6"')
print(s[max(0, i - 400):i + 1200])
print("=== vo p6 files")
d = os.path.join(HERE, "vn2", "audio", "vo")
for n in sorted(os.listdir(d)):
    if n.startswith("p6"):
        print(" ", n, os.path.getsize(os.path.join(d, n)))
print("=== voices.json")
vj = os.path.join(d, "_voices.json")
if os.path.exists(vj):
    j = json.load(open(vj, encoding="utf-8"))
    for k in sorted(j):
        if k.startswith("p6"):
            print(" ", k, j[k])
