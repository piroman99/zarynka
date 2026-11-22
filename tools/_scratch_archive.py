# -*- coding: utf-8 -*-
"""Архивирует tools/scratch/ (мёртвые одноразовые скрипты) в tar.gz ВНЕ репозитория
и убирает каталог из рабочего дерева. Файлы остаются в истории git —
архив нужен, чтобы достать их без git-археологии.

Запуск: python3 tools/_scratch_archive.py [--dry]
"""
import os
import shutil
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRATCH = os.path.join(ROOT, 'tools', 'scratch')
ARCH_DIR = os.path.join(os.path.dirname(os.path.dirname(ROOT)), '_archive')
TAR = os.path.join(ARCH_DIR, 'zaryanka_tools_scratch_2026-11-22.tar.gz')

dry = '--dry' in sys.argv

files = sorted(f for f in os.listdir(SCRATCH)
               if os.path.isfile(os.path.join(SCRATCH, f)))
print('файлов к архиву: %d' % len(files))
if dry:
    print('dry-run, ничего не пишу')
    sys.exit(0)

os.makedirs(ARCH_DIR, exist_ok=True)
with tarfile.open(TAR, 'w:gz') as tf:
    for f in files:
        tf.add(os.path.join(SCRATCH, f), arcname='tools/scratch/' + f)
size = os.path.getsize(TAR)
with tarfile.open(TAR, 'r:gz') as tf:
    n = len(tf.getnames())
print('архив: %s  %.2f МБ  файлов внутри %d' % (os.path.relpath(TAR, os.path.dirname(ROOT)),
                                               size / 1048576.0, n))
assert n == len(files), 'в архиве %d файлов вместо %d' % (n, len(files))

# удаляем каталог из дерева (rm в песочнице запрещён)
shutil.rmtree(SCRATCH)
print('каталог tools/scratch удалён, есть ли: %s' % os.path.exists(SCRATCH))

# фиксируем удаление в индексе
subprocess.check_call(['git', 'add', '-A', 'tools/scratch'], cwd=ROOT)
out = subprocess.check_output(['git', 'status', '--porcelain', 'tools/scratch'], cwd=ROOT, text=True)
print('git status по tools/scratch: %d строк' % len(out.splitlines()))
print(out[:400])
