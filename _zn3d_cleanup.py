# -*- coding: utf-8 -*-
"""Уборка после пересборки значка: временные кадры, дубли, диагностические скрипты."""
import os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))

dirs = ['.tmp_znakB', '.tmp_swapcheck', '.tmp_znak3d']
for d in dirs:
    p = os.path.join(HERE, d)
    if os.path.isdir(p):
        n = sum(len(f) for _, _, f in os.walk(p))
        shutil.rmtree(p)
        print('удалён каталог', d, '(%d файлов)' % n)

files = [
    'out/znak3d_rot_B.mp4',           # дубль финала
    '_znchek_peek.py', '_znchek_diff.py', '_znchek_geom.py',
    '_zn3d_diag.py', '_zn3d_diag2.py', '_zn3d_plmiss.py', '_zn3d_headcmp.py',
    '_zn3d_fetchprobe.py', '_zn3d_http.py', '_zn3d_sharp.py', '_zn3d_edge.py',
    '_zn3d_rim.py', '_zn3d_angles.py', '_zn3d_check_B.py',
    'assets/review/_znchek_0.6.png', 'assets/review/_znchek_3.0.png',
    'assets/review/_znchek_4.5.png', 'assets/review/_znchek_4.9.png',
    'assets/review/_znchek_5.3.png',
    'assets/review/_znB_t0.0.png', 'assets/review/_znB_t1.0.png',
    'assets/review/_znB_t1.4.png', 'assets/review/_znB_t1.9.png',
    'assets/review/_znB_t2.6.png', 'assets/review/_znB_t4.0.png',
    'assets/review/_znB_t4.6.png', 'assets/review/_znB_t5.3.png',
    'assets/review/_znBv_0.0.png', 'assets/review/_znBv_1.4.png',
    'assets/review/_znBv_4.0.png', 'assets/review/_znBv_5.3.png',
]
for f in files:
    p = os.path.join(HERE, f)
    if os.path.exists(p):
        os.remove(p)
        print('удалён', f)

# стиллы-варианты (нужны были только для выбора)
for nm in ('A', 'B', 'C'):
    for ang in ('000', '090', '180'):
        p = os.path.join(HERE, 'assets', 'review', '_zn2_%s_%s.png' % (nm, ang))
        if os.path.exists(p):
            os.remove(p)
print('стиллы вариантов A/B/C убраны')
print('осталось в out/:', sorted(x for x in os.listdir(os.path.join(HERE, 'out')) if x.endswith('.mp4')))
