# -*- coding: utf-8 -*-
"""Последняя уборка корня: сообщения коммитов и временные снимки — в подкаталоги.

.git_msg*.txt      -> .git_msg/          (это только тексты для git commit -F)
_tmp_title_*.png   -> _sat/title/        (проверочные снимки, ссылок нет)
_vo_dup.txt        -> _sat/
_pv_*.json/.txt, scenario.json остаются: на них ссылаются живые инструменты.
"""
import glob
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def mv(src_rel, dst_dir):
    src = os.path.join(ROOT, src_rel)
    if not os.path.exists(src):
        return None
    os.makedirs(os.path.join(ROOT, dst_dir), exist_ok=True)
    r = subprocess.run(['git', 'mv', src_rel, os.path.join(dst_dir, src_rel)],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode == 0:
        return 'git mv -> ' + dst_dir
    dst = os.path.join(ROOT, dst_dir, os.path.basename(src_rel))
    os.replace(src, dst)
    return 'move -> ' + dst_dir


for name in sorted(glob.glob(os.path.join(ROOT, '.git_msg*.txt'))):
    base = os.path.basename(name)
    print('%-34s %s' % (base, mv(base, '.git_msg')))
for name in sorted(glob.glob(os.path.join(ROOT, '_tmp_title_*.png'))):
    base = os.path.basename(name)
    print('%-34s %s' % (base, mv(base, os.path.join('_sat', 'title'))))
print('%-34s %s' % ('_vo_dup.txt', mv('_vo_dup.txt', '_sat')))

left = sorted(f for f in os.listdir(ROOT) if os.path.isfile(os.path.join(ROOT, f)))
print('\nфайлов в корне осталось: %d' % len(left))
for f in left:
    print('  ' + f)
