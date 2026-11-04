# -*- coding: utf-8 -*-
import os, time
HERE = os.path.dirname(os.path.abspath(__file__))
for rel in ["_vn2_build.py", "_vn2_cg_range.py", "_prolog_finals.py", "vn2/content.js"]:
    p = os.path.join(HERE, rel)
    print("%-20s %s" % (rel, time.strftime("%m-%d %H:%M", time.localtime(os.path.getmtime(p)))))
d = os.path.join(HERE, "assets", "final", "prolog")
for n in sorted(os.listdir(d)):
    p = os.path.join(d, n)
    print("  %-16s %8d %s" % (n, os.path.getsize(p), time.strftime("%m-%d %H:%M", time.localtime(os.path.getmtime(p)))))
print("now", time.strftime("%m-%d %H:%M"))
