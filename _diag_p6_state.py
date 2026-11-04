# -*- coding: utf-8 -*-
import os, json, re, time
HERE = os.path.dirname(os.path.abspath(__file__))
for rel in ["_prolog_p6_final.py", "_p6_final.py", "_prolog_final_p6.py"]:
    print(rel, os.path.exists(os.path.join(HERE, rel)))
print("--- vn2/img/prolog")
d = os.path.join(HERE, "vn2", "img", "prolog")
for n in sorted(os.listdir(d)):
    p = os.path.join(d, n)
    print("  %-14s %8d %s" % (n, os.path.getsize(p), time.strftime("%m-%d %H:%M", time.localtime(os.path.getmtime(p)))))
print("--- content.js nodes")
s = open(os.path.join(HERE, "vn2", "content.js"), encoding="utf-8").read()
print("len", len(s))
m = re.search(r"nodes\s*[:=]\s*\[", s)
print("nodes at", m.start() if m else None)
for nm in ["'p6'", '"p6"']:
    print(nm, s.count(nm))
# вывести id сцен
print(re.findall(r'id:\s*"([a-z0-9_]+)"', s)[:20])
print("--- files list")
print(sorted(os.listdir(HERE))[-1:])
