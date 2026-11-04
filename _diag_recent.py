# -*- coding: utf-8 -*-
"""Что менялось в проекте за последние 60 минут (кроме vn2/img, vn2/audio)."""
import os, time
HERE = os.path.dirname(os.path.abspath(__file__))
now = time.time()
rows = []
skip = {".git", "__pycache__", "_sat", "assets/gen", "assets/rejected", "vn2/img", "node_modules"}
for root, dirs, files in os.walk(HERE):
    dirs[:] = [d for d in dirs if d not in skip and not d.startswith(".")]
    for fn in files:
        p = os.path.join(root, fn)
        try:
            mt = os.path.getmtime(p)
        except OSError:
            continue
        if now - mt < 3600:
            rows.append((mt, os.path.relpath(p, HERE), os.path.getsize(p)))
for mt, rel, sz in sorted(rows):
    print("%s %10d %s" % (time.strftime("%H:%M:%S", time.localtime(mt)), sz, rel))
