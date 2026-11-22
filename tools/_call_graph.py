# -*- coding: utf-8 -*-
"""Кто кого запускает по имени (subprocess) и кто кого импортирует — до переноса.

Ищем в скриптах корня:
  * запуск другого скрипта: 'python3', '_x.py'  /  "python3 _x.py"
  * импорт локального модуля: import _x  /  from _x import
Печатаем пары и вердикт: останутся ли они в одном каталоге после переноса.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
SPAWN = re.compile(r"""['"]python3['"]\s*,\s*['"](_[A-Za-z0-9_]+\.py)['"]""")
SPAWN2 = re.compile(r"""python3\s+(_[A-Za-z0-9_]+\.py)""")
IMP = re.compile(r'^\s*(?:import|from)\s+(_[A-Za-z0-9_]+)\b', re.M)

rows = []
for name in sorted(os.listdir(HERE)):
    if not name.endswith('.py') or not name.startswith('_'):
        continue
    p = os.path.join(HERE, name)
    try:
        if os.path.getsize(p) > 2_000_000:
            continue
        with open(p, encoding='utf-8', errors='ignore') as f:
            txt = f.read()
    except OSError:
        continue
    for m in set(SPAWN.findall(txt)) | set(SPAWN2.findall(txt)):
        if m != name and os.path.exists(os.path.join(HERE, m)):
            rows.append(('spawn', name, m))
    for m in set(IMP.findall(txt)):
        cand = m + '.py'
        if cand != name and os.path.exists(os.path.join(HERE, cand)):
            rows.append(('import', name, m + '.py'))

print('связей найдено: %d' % len(rows))
print('  spawn : %d' % sum(1 for r in rows if r[0] == 'spawn'))
print('  import: %d' % sum(1 for r in rows if r[0] == 'import'))
print('\nпервые 25:')
for kind, a, b in rows[:25]:
    print('  %-7s %-34s -> %s' % (kind, a, b))
