# -*- coding: utf-8 -*-
"""Починка уже перенесённых скриптов: правильная глубина ROOT для их каталога."""
import os
import py_compile
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import _move_tools as mt  # noqa: E402


def main():
    base = os.path.join(HERE, 'tools')
    fixed = 0
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        rel = os.path.relpath(root, HERE)
        depth = rel.count(os.sep) + 1
        for f in files:
            if not f.endswith('.py'):
                continue
            p = os.path.join(root, f)
            with open(p, encoding='utf-8') as fh:
                txt = fh.read()
            new, info = mt.fix_text(txt, depth)
            if new != txt:
                with open(p, 'w', encoding='utf-8') as fh:
                    fh.write(new)
                fixed += 1
            py_compile.compile(p, doraise=True)
            bad = mt.audit(p)
            print('%-40s depth=%d %s%s' % (rel + '/' + f, depth, info,
                                           ('  АУДИТ: нет ' + ', '.join(sorted(set(bad)))) if bad else ''))
    print('\nпоправлено файлов: %d' % fixed)


if __name__ == '__main__':
    main()
