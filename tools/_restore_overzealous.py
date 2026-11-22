# -*- coding: utf-8 -*-
"""Возврат переосторожно вынесенных скриптов обратно в репозиторий.

Отсев был слишком широким: путь /home/ivan — это просто каталог, в котором
скрипты писались, он ничего не выдаёт. Держим вне репозитория только файлы с
действительно приватным: IP домашней станции (192.168.*) и логин на ней.
Остальные возвращаем: в tools/ — если на них ссылаются документация или живые
скрипты, иначе в tools/scratch/.
"""
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WS = os.path.dirname(os.path.dirname(ROOT))
SRC = os.path.join(WS, '_station_scripts')

SECRET = re.compile(r'192\.168\.\d+\.\d+')
OWN = ('_privacy_sweep.py', '_restore_overzealous.py', '_restore_push.py',
       '_show_stay.py', '_bring_back_helpers.py', '_secrets_scan.py')
TOKEN = re.compile(r'[A-Za-z0-9_][A-Za-z0-9_.-]*\.(?:py|sh)')

if not os.path.isdir(SRC):
    print('нет каталога', SRC)
    raise SystemExit(1)

# упоминания внутри репозитория
mentions = set()
for base, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', '_sat', 'assets')]
    for f in files:
        if not f.endswith(('.py', '.md', '.json', '.html', '.txt', '.js')):
            continue
        p = os.path.join(base, f)
        try:
            if os.path.getsize(p) > 2_000_000:
                continue
            with open(p, encoding='utf-8', errors='ignore') as fh:
                mentions |= set(TOKEN.findall(fh.read()))
        except OSError:
            continue

stay, back_live, back_scratch = [], [], []
for name in sorted(os.listdir(SRC)):
    p = os.path.join(SRC, name)
    if not os.path.isfile(p):
        continue
    try:
        with open(p, encoding='utf-8', errors='ignore') as fh:
            txt = fh.read()
    except OSError:
        continue
    if name not in OWN and SECRET.search(txt):
        stay.append(name)
        continue
    (back_live if name in mentions else back_scratch).append((name, p))

for name, p in back_live:
    dst = os.path.join(HERE, name)
    if not os.path.exists(dst):
        shutil.move(p, dst)
for name, p in back_scratch:
    dst = os.path.join(HERE, 'scratch', name)
    if not os.path.exists(dst):
        shutil.move(p, dst)

print('осталось вне репозитория (станционное): %d' % len(stay))
for n in stay:
    print('   ' + n)
print('возвращено в tools/: %d, в tools/scratch/: %d' % (len(back_live), len(back_scratch)))
print('итого: tools %d .py, scratch %d .py'
      % (len([f for f in os.listdir(HERE) if f.endswith('.py')]),
         len([f for f in os.listdir(os.path.join(HERE, 'scratch')) if f.endswith('.py')])))
