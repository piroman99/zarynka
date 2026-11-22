# -*- coding: utf-8 -*-
"""Проверка после уборки корня.

1) аудит: все os.path.join(ROOT, 'X') в tools/**/*.py указывают на существующее;
2) импорт общих модулей из tools/ (pv, _vn2_nodes, _cdp);
3) запуск живого скрипта, который читает репо-файлы (проверка, что ROOT верный).
"""
import os
import py_compile
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def audit_all():
    bad_total = 0
    checked = 0
    for base, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for f in files:
            if not f.endswith('.py'):
                continue
            p = os.path.join(base, f)
            with open(p, encoding='utf-8') as fh:
                txt = fh.read()
            checked += 1
            py_compile.compile(p, doraise=True)
            for m in re.finditer(r"os\.path\.join\(ROOT,\s*['\"]([A-Za-z0-9_./-]+)['\"]", txt):
                lit = m.group(1)
                if not os.path.exists(os.path.join(ROOT, lit)):
                    print('  БИТЫЙ ПУТЬ %s: %s' % (os.path.relpath(p, ROOT), lit))
                    bad_total += 1
    print('проверено файлов: %d, битых ROOT-путей: %d' % (checked, bad_total))
    return bad_total


def imports():
    sys.path.insert(0, HERE)
    ok = []
    for mod in ('pv', '_vn2_nodes', '_move_tools'):
        try:
            __import__(mod)
            ok.append(mod)
        except Exception as e:
            print('  импорт %s упал: %s: %s' % (mod, type(e).__name__, e))
    print('импортируются из tools/: %s' % ', '.join(ok))


def run_live():
    """_poet_measure.py живёт в tools/alley и читает vn2/ и _sat/ через ROOT."""
    import subprocess
    p = os.path.join(HERE, 'alley', '_poet_measure.py')
    r = subprocess.run(['python3', '_poet_measure.py'], cwd=os.path.dirname(p),
                       capture_output=True, text=True, timeout=300)
    tail = [l for l in r.stdout.strip().splitlines() if 'контроль' in l or 'H =' in l]
    print('запуск tools/alley/_poet_measure.py: rc=%d' % r.returncode)
    for l in tail:
        print('   ' + l.strip())
    if r.returncode != 0:
        print(r.stderr[-800:])


if __name__ == '__main__':
    bad = audit_all()
    imports()
    run_live()
    sys.exit(0 if bad == 0 else 1)
