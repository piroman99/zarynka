# -*- coding: utf-8 -*-
"""Есть ли промах предзагрузки тизера ДО моих правок: бэкап/откат/возврат vn2."""
import os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BAK = os.path.join(HERE, '.tmp_mob', 'bak_vn2')
FILES = ['app.js', 'index.html', 'style.css']
mode = sys.argv[1] if len(sys.argv) > 1 else 'bak'


def run(*a):
    p = subprocess.run(a, cwd=HERE, capture_output=True, text=True)
    print(' '.join(a), '->', p.returncode, p.stdout.strip()[:300], p.stderr.strip()[:300])


if mode == 'bak':
    os.makedirs(BAK, exist_ok=True)
    for f in FILES:
        shutil.copy2(os.path.join(HERE, 'vn2', f), os.path.join(BAK, f))
    print('backup ->', BAK)
elif mode == 'revert':
    run('git', 'checkout', '--', 'vn2/app.js', 'vn2/index.html', 'vn2/style.css')
elif mode == 'restore':
    for f in FILES:
        shutil.copy2(os.path.join(BAK, f), os.path.join(HERE, 'vn2', f))
    print('restored from', BAK)
