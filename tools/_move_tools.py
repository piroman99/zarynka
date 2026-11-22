# -*- coding: utf-8 -*-
"""Перенос скриптов из корня в подкаталог с автоматической починкой путей.

Что делает для каждого файла:
  1) git mv <root>/<name> <root>/<dst>/<name>   (история сохраняется);
  2) в тексте: после строки HERE = ... добавляет ROOT = os.path.dirname(HERE),
     если его ещё нет;
  3) заменяет os.path.join(HERE, '<репо-каталог>', ...) на ROOT — только для
     известных каталогов репозитория;
  4) py_compile каждого файла после правки;
  5) аудит: для каждого os.path.join(ROOT, 'X', ...) проверяет, что X существует.

Запуск: python3 _move_tools.py <dst_dir> file1.py file2.py ...
"""
import os
import py_compile
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


ROOT = os.path.dirname(HERE)
REPO_DIRS = ('assets', 'vn2', 'out', 'refs', 'data', '_sat', 'scripts', 'tests', 'keys',
             'teaser_lyod', 'logo', 'canvas', 'review')

HERE_RE = re.compile(r'^(\s*)HERE\s*=\s*os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\s*$',
                     re.M)
ROOT_DEF = re.compile(r'^\s*ROOT\s*=', re.M)


def fix_text(txt, depth=1):
    if not HERE_RE.search(txt):
        return txt, 'нет HERE'
    expr = 'os.path.dirname(' * depth + 'HERE' + ')' * depth
    root_line = re.compile(r'^\s*ROOT\s*=.*$', re.M)
    if root_line.search(txt):
        txt = root_line.sub('ROOT = ' + expr, txt, count=1)
    else:
        txt = HERE_RE.sub(lambda m: m.group(0) + '\n' + m.group(1) + 'ROOT = ' + expr,
                          txt, count=1)
    n = 0
    for d in REPO_DIRS:
        for sep in ("'", '"'):
            pat = "os.path.join(HERE, %s%s%s" % (sep, d, sep)
            rep = "os.path.join(ROOT, %s%s%s" % (sep, d, sep)
            if pat in txt:
                n += txt.count(pat)
                txt = txt.replace(pat, rep)
    return txt, '%d путей' % n


def repo_root_of(path):
    d = os.path.dirname(os.path.abspath(path))
    for _ in range(8):
        if os.path.exists(os.path.join(d, '.git')):
            return d
        d = os.path.dirname(d)
    return os.path.dirname(os.path.dirname(path))


def audit(path):
    with open(path, encoding='utf-8') as f:
        txt = f.read()
    root = repo_root_of(path)
    bad = []
    for m in re.finditer(r"os\.path\.join\(ROOT,\s*['\"]([A-Za-z0-9_./-]+)['\"]", txt):
        lit = m.group(1)
        if not os.path.exists(os.path.join(root, lit)):
            bad.append(lit)
    return bad


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    dst = sys.argv[1].strip('/')
    names = sys.argv[2:]
    depth = dst.count('/') + 1
    target_dir = os.path.join(HERE, dst)
    os.makedirs(target_dir, exist_ok=True)

    moved, failed = [], []
    for name in names:
        src = os.path.join(HERE, name)
        if not os.path.exists(src):
            failed.append((name, 'нет файла'))
            continue
        rel = os.path.join(dst, name)
        r = subprocess.run(['git', 'mv', name, rel], cwd=HERE,
                           capture_output=True, text=True)
        if r.returncode != 0:
            # файл мог быть не в индексе (untracked) — тогда обычное перемещение
            try:
                os.replace(src, os.path.join(target_dir, name))
            except OSError as e:
                failed.append((name, str(e)))
                continue
        dst_path = os.path.join(target_dir, name)
        try:
            with open(dst_path, encoding='utf-8') as f:
                txt = f.read()
            new, info = fix_text(txt, depth)
            if new != txt:
                with open(dst_path, 'w', encoding='utf-8') as f:
                    f.write(new)
            py_compile.compile(dst_path, doraise=True)
            bad = audit(dst_path)
            moved.append((name, info, bad))
        except Exception as e:
            failed.append((name, '%s: %s' % (type(e).__name__, e)))

    print('перенесено: %d, проблем: %d' % (len(moved), len(failed)))
    for name, info, bad in moved:
        flag = ('  АУДИТ: нет %s' % ', '.join(sorted(set(bad)))) if bad else ''
        print('  %-34s %s%s' % (name, info, flag))
    for name, why in failed:
        print('  ОШИБКА %-28s %s' % (name, why))
    return 0 if not failed else 2


if __name__ == '__main__':
    sys.exit(main())
