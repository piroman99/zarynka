# -*- coding: utf-8 -*-
"""Печать всех реплик (строк, начинающихся с тире) с номерами строк."""
import io
import sys

start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
stop = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 6
lines = io.open('assets/story.txt', encoding='utf-8').read().split('\n')
for i, ln in enumerate(lines, 1):
    if not (start <= i <= stop):
        continue
    t = ln.strip()
    if t.startswith('\u2014'):
        print('%d: %s' % (i, t))
        print()
