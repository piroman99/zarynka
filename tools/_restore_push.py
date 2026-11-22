# -*- coding: utf-8 -*-
"""Возврат push-скриптов: адрес nanobot@karpoukhin.ru заменяем на публичный
piroman99@yandex.ru (он и так в истории репозитория), станционные — оставляем вне."""
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(os.path.dirname(os.path.dirname(ROOT)), '_station_scripts')

OLD = 'nanobot@karpoukhin.ru'
NEW = 'piroman99@yandex.ru'
STATION = re.compile(r'192\.168\.\d+\.\d+')

back, left = [], []
for name in sorted(os.listdir(SRC)):
    p = os.path.join(SRC, name)
    if not os.path.isfile(p):
        continue
    with open(p, encoding='utf-8', errors='ignore') as fh:
        txt = fh.read()
    if STATION.search(txt):
        left.append(name)
        continue
    if OLD in txt:
        txt = txt.replace(OLD, NEW)
        with open(p, 'w', encoding='utf-8') as fh:
            fh.write(txt)
    dst = os.path.join(HERE, name)
    if os.path.exists(dst):
        left.append(name + ' (уже есть)')
        continue
    shutil.move(p, dst)
    back.append(name)

print('возвращено: %d' % len(back))
print('осталось вне (станция): %d -> %s' % (len(left), ', '.join(left)))
print('итого tools: %d .py' % len([f for f in os.listdir(HERE) if f.endswith('.py')]))
