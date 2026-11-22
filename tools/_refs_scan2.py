# -*- coding: utf-8 -*-
"""Обратный скан: собираем все упоминания имён скриптов в текстах репо, потом
сверяем с файлами корня. Быстро: один проход по файлам, без O(n^2) регексов.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKIP_DIRS = {'.git', '__pycache__', '.probe', '.tools', '_sat', 'assets'}
EXT = ('.py', '.md', '.json', '.html', '.js', '.sh', '.txt', '.yml')
MAXB = 3 * 1024 * 1024

TOKEN = re.compile(r'[A-Za-z0-9_][A-Za-z0-9_.-]*\.(?:py|sh)')


def main():
    mentions = {}
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if not f.endswith(EXT):
                continue
            p = os.path.join(base, f)
            try:
                if os.path.getsize(p) > MAXB:
                    continue
                with open(p, encoding='utf-8', errors='ignore') as fh:
                    txt = fh.read()
            except OSError:
                continue
            for m in set(TOKEN.findall(txt)):
                if m == f:
                    continue
                mentions.setdefault(m, set()).add(os.path.relpath(p, ROOT))

    root_scripts = sorted(f for f in os.listdir(ROOT)
                          if os.path.isfile(os.path.join(ROOT, f))
                          and f.endswith(('.py', '.sh')))
    alive = [(f, sorted(mentions[f])[:3], len(mentions[f]))
             for f in root_scripts if f in mentions]
    orphan = [f for f in root_scripts if f not in mentions]

    print('скриптов в корне: %d; живых %d; сирот %d'
          % (len(root_scripts), len(alive), len(orphan)))
    print('\n=== ЖИВЫЕ:')
    for f, hits, n in alive:
        print('  %-44s x%-3d <- %s' % (f, n, ', '.join(hits)))
    print('\n=== СИРОТЫ (%d):' % len(orphan))
    for f in orphan:
        print('  ' + f)


if __name__ == '__main__':
    main()
