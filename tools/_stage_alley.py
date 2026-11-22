# -*- coding: utf-8 -*-
"""Коммит сцены «аллея»: явный список файлов, без `git add -A`."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


ROOT = os.path.dirname(HERE)
FILES = [
    'vn2/img/char/poet_seat_upset.webp',
    'assets/sprites/prop_bench_blender.png',
    'assets/gen/alley_b_nobench__gpt-image-2_0.png',
    'STATUS.md',
    'tools/alley/_bench_blend7.py',
    'tools/alley/_bench_blend_diag.py',
    'tools/alley/_bench_wc.py',
    'tools/alley/_bench_compose3.py',
    'tools/alley/_alley_final2.py',
    'tools/alley/_alley_scale.py',
    'tools/alley/_poet_measure.py',
    'tools/alley/_poet_defringe.py',
    'tools/alley/_bench_geom_v7.py',
    'tools/alley/_bench_bolts_check.py',
    'tools/alley/_bench_prop_preview.py',
]


def run(*args, **kw):
    r = subprocess.run(args, cwd=HERE, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print('FAIL', ' '.join(args))
        print(r.stdout[-2000:])
        print(r.stderr[-2000:])
    return r


for f in FILES:
    if not os.path.exists(os.path.join(HERE, f)):
        print('НЕТ ФАЙЛА:', f)
        continue
    r = run('git', 'add', '--', f)
    if r.returncode == 0:
        print('добавлен', f)

print('\n--- в индексе:')
print(run('git', 'diff', '--cached', '--name-status').stdout)
