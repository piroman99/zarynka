# -*- coding: utf-8 -*-
"""Кто в корне репозитория на кого ссылается.

Для каждого файла корня ищем его имя в остальных файлах репо (py/md/json/html).
Печатаем: файл, сколько раз упомянут, кем именно (первые 3), и вердикт
«живой» (кто-то зовёт) или «сирота» (можно двигать/удалять без риска).
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SKIP_DIRS = {'.git', '__pycache__', '.probe', '.tools', 'node_modules', '_sat'}
TEXT_EXT = ('.py', '.md', '.json', '.html', '.js', '.sh', '.txt')


def walk():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.git')]
        for f in files:
            if f.endswith(TEXT_EXT):
                yield os.path.join(base, f)


def main():
    root_files = [f for f in os.listdir(ROOT)
                  if os.path.isfile(os.path.join(ROOT, f)) and not f.startswith('.git_msg')]
    corpus = {}
    for p in walk():
        try:
            with open(p, encoding='utf-8', errors='ignore') as fh:
                corpus[p] = fh.read()
        except OSError:
            pass
    print('файлов в корне: %d, прочитано текстов: %d' % (len(root_files), len(corpus)))

    alive, orphan = [], []
    for name in sorted(root_files):
        if not name.endswith(('.py', '.sh')):
            continue
        pat = re.compile(r'(?<![\w/.-])' + re.escape(name))
        hits = []
        for p, txt in corpus.items():
            if os.path.basename(p) == name and os.path.dirname(p) == ROOT:
                continue
            if pat.search(txt):
                hits.append(os.path.relpath(p, ROOT))
        (alive if hits else orphan).append((name, hits))

    print('\n=== ЖИВЫЕ (на них ссылаются), %d:' % len(alive))
    for name, hits in alive:
        print('  %-42s <- %s' % (name, ', '.join(hits[:3]) + (' …' if len(hits) > 3 else '')))
    print('\n=== СИРОТЫ (никто не зовёт), %d:' % len(orphan))
    for name, _ in orphan:
        print('  %s' % name)


if __name__ == '__main__':
    main()
