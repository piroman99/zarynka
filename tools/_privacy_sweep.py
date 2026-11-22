# -*- coding: utf-8 -*-
"""Ищем в tools/ файлы с приватными путями/адресами и выносим их из репозитория.

Репозиторий публичный: IP домашней станции, пути /home/ivan, /home/nanobot и
адрес 2mon.ru в нём не нужны. Такие файлы — не про «Зарянку», а про станцию,
их место в workspace.
"""
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WS = os.path.dirname(os.path.dirname(ROOT))     # workspace
OUTDIR = os.path.join(WS, '_station_scripts')

PAT = re.compile(r'192\.168\.\d+\.\d+|nanobot@')

found = []
for base, dirs, files in os.walk(HERE):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in files:
        if not f.endswith(('.py', '.sh', '.md', '.json', '.txt')):
            continue
        p = os.path.join(base, f)
        try:
            if os.path.getsize(p) > 2_000_000:
                continue
            with open(p, encoding='utf-8', errors='ignore') as fh:
                txt = fh.read()
        except OSError:
            continue
        if PAT.search(txt):
            found.append((p, sorted(set(PAT.findall(txt)))))

print('файлов с приватным: %d' % len(found))
for p, hits in found:
    print('  %-52s %s' % (os.path.relpath(p, ROOT), ', '.join(hits)))

os.makedirs(OUTDIR, exist_ok=True)
moved = 0
for p, _ in found:
    dst = os.path.join(OUTDIR, os.path.basename(p))
    n = 1
    while os.path.exists(dst):
        stem, ext = os.path.splitext(os.path.basename(p))
        dst = os.path.join(OUTDIR, '%s_%d%s' % (stem, n, ext))
        n += 1
    shutil.move(p, dst)
    moved += 1
print('\nвынесено в workspace/_station_scripts: %d' % moved)
