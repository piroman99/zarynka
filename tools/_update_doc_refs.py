# -*- coding: utf-8 -*-
"""Обновление ссылок на скрипты в документации после переноса в tools/.

Заменяем `_name.py` -> `tools/_name.py` (живые) и `_name.py` -> `tools/scratch/_name.py`
(мёртвые). Не трогаем уже префиксованные пути, .git_msg* и сами скрипты.

Режим: python3 _update_doc_refs.py plan | apply
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def collect():
    live = {f for f in os.listdir(HERE) if f.endswith(('.py', '.sh'))}
    scratch = set()
    sd = os.path.join(HERE, 'scratch')
    if os.path.isdir(sd):
        scratch = {f for f in os.listdir(sd) if f.endswith(('.py', '.sh'))}
    return live, scratch


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'plan'
    live, scratch = collect()
    print('живых скриптов: %d, мёртвых: %d' % (len(live), len(scratch)))

    docs = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', '_sat', 'assets')]
        for f in files:
            if f.endswith('.md') and not f.startswith('.'):
                docs.append(os.path.join(base, f))

    total = 0
    for p in docs:
        with open(p, encoding='utf-8') as fh:
            txt = fh.read()
        orig = txt
        n = 0
        for group, prefix in ((live, 'tools/'), (scratch, 'tools/scratch/')):
            for name in sorted(group, key=len, reverse=True):
                pat = re.compile(r'(?<![\w/.-])' + re.escape(name) + r'(?![\w-])')
                if not pat.search(txt):
                    continue
                # не префиксуем то, что уже идёт после tools/
                def repl(m):
                    return prefix + m.group(0)
                new, cnt = pat.subn(repl, txt)
                if cnt:
                    txt, n = new, n + cnt
        if txt != orig:
            total += n
            print('  %-46s %d ссылок' % (os.path.relpath(p, ROOT), n))
            if mode == 'apply':
                with open(p, 'w', encoding='utf-8') as fh:
                    fh.write(txt)
    print('всего ссылок: %d (%s)' % (total, 'записано' if mode == 'apply' else 'план'))


if __name__ == '__main__':
    main()
