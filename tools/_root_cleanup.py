# -*- coding: utf-8 -*-
"""Большая уборка корня репозитория: скрипты -> tools/ (живые) и tools/scratch/ (мёртвые).

Правила:
  * «живой» = упомянут в документации/текстах репо ИЛИ импортируется/запускается
    живым скриптом (транзитивное замыкание). Такие -> tools/, плоско: они
    импортируют друг друга по имени, и один каталог сохраняет импорты рабочими.
  * «мёртвый» = никто не упоминает и не зовёт -> tools/scratch/.
  * пути внутри файлов: HERE остаётся каталогом файла, добавляется ROOT нужной
    глубины, репо-каталоги (assets, vn2, out, ...) переключаются на ROOT.
  * после переноса: py_compile каждого файла + аудит, что ROOT-пути существуют.

Режим: python3 _root_cleanup.py plan   (только показать)
       python3 _root_cleanup.py apply  (перенести)
"""
import os
import py_compile
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import _move_tools as mt  # noqa: E402

SKIP_DIRS = {'.git', '__pycache__', '.probe', '.tools', '_sat', 'assets', '_shots_vn',
             '_wt', '_pylib', '_tmp_sprite_review', 'node_modules'}
TEXT_EXT = ('.py', '.md', '.json', '.html', '.js', '.txt', '.yml')
MAXB = 2 * 1024 * 1024
TOKEN = re.compile(r'[A-Za-z0-9_][A-Za-z0-9_.-]*\.(?:py|sh)')


def repo_texts():
    """тексты репо, кроме корневых скриптов: они задают «живость»."""
    for base, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if not f.endswith(TEXT_EXT) or f.startswith('.git_msg'):
                continue
            p = os.path.join(base, f)
            if os.path.dirname(p) == HERE and f.endswith(('.py', '.sh')):
                continue
            try:
                if os.path.getsize(p) > MAXB:
                    continue
                with open(p, encoding='utf-8', errors='ignore') as fh:
                    yield p, fh.read()
            except OSError:
                continue


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'plan'
    root_scripts = sorted(f for f in os.listdir(HERE)
                          if os.path.isfile(os.path.join(HERE, f))
                          and f.endswith(('.py', '.sh'))
                          and not f.startswith(('_root_cleanup', '_move_tools',
                                                '_fix_tools_paths', '_stage_alley',
                                                '_call_graph', '_refs_scan')))
    print('скриптов в корне: %d' % len(root_scripts))

    # 1) упоминания из «внешних» текстов (docs, vn2, tests) — это семена
    seeds = set()
    for p, txt in repo_texts():
        for tok in TOKEN.findall(txt):
            if tok in root_scripts:
                seeds.add(tok)
    print('семян из документации и соседних каталогов: %d' % len(seeds))

    # 2) граф упоминаний внутри корневых скриптов
    graph = {}
    for name in root_scripts:
        try:
            with open(os.path.join(HERE, name), encoding='utf-8', errors='ignore') as fh:
                txt = fh.read()
        except OSError:
            continue
        graph[name] = {t for t in TOKEN.findall(txt) if t in root_scripts and t != name}

    # 3) транзитивное замыкание + защищённые шаблоны (ими пользуемся руками:
    #    пуш, тесты движка, клиенты API) — такие остаются в tools/ всегда
    PROTECT = ('_gh_', '_push_', '_vn2_', '_pl_', 'pv', 'vk', 'tg', '_cdp',
               '_bench_', '_alley_', '_poet_', '_kate_', '_cast_', '_audio', '_vo_')
    live = set(seeds)
    live |= {n for n in root_scripts if n.startswith(PROTECT)}
    stack = list(seeds)
    while stack:
        cur = stack.pop()
        for nxt in graph.get(cur, ()):
            if nxt not in live:
                live.add(nxt)
                stack.append(nxt)
    dead = [n for n in root_scripts if n not in live]
    print('живых: %d, мёртвых: %d' % (len(live), len(dead)))

    if mode == 'plan':
        print('\nмёртвые (первые 40):')
        for n in dead[:40]:
            print('  ' + n)
        print('\nживые (первые 40):')
        for n in sorted(live)[:40]:
            print('  ' + n)
        return 0

    # 4) перенос
    moved_live = move_group([n for n in root_scripts if n in live], 'tools', 1)
    moved_dead = move_group(dead, 'tools/scratch', 2)
    print('\nперенесено: живых %d в tools/, мёртвых %d в tools/scratch/'
          % (moved_live, moved_dead))
    print('осталось скриптов в корне: %d'
          % len([f for f in os.listdir(HERE) if f.endswith(('.py', '.sh'))]))
    return 0


def move_group(names, dst, depth):
    ok = 0
    target_dir = os.path.join(HERE, dst)
    os.makedirs(target_dir, exist_ok=True)
    for name in names:
        src = os.path.join(HERE, name)
        if not os.path.exists(src):
            continue
        rel = os.path.join(dst, name)
        r = subprocess.run(['git', 'mv', name, rel], cwd=HERE, capture_output=True, text=True)
        if r.returncode != 0:
            try:
                os.replace(src, os.path.join(target_dir, name))
            except OSError as e:
                print('  ОШИБКА %s: %s' % (name, e))
                continue
        p = os.path.join(target_dir, name)
        if name.endswith('.py'):
            try:
                with open(p, encoding='utf-8') as f:
                    txt = f.read()
                new, _ = mt.fix_text(txt, depth)
                if depth >= 2:
                    # скрипты из tools/scratch/ должны видеть общие модули из tools/
                    for old in ("sys.path.insert(0, HERE)", "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))"):
                        if old in new:
                            new = new.replace(old, "sys.path.insert(0, os.path.join(ROOT, 'tools'))")
                if new != txt:
                    with open(p, 'w', encoding='utf-8') as f:
                        f.write(new)
                py_compile.compile(p, doraise=True)
            except Exception as e:
                print('  НЕ КОМПИЛИРУЕТСЯ %s: %s: %s' % (name, type(e).__name__, e))
                continue
        ok += 1
    return ok


if __name__ == '__main__':
    sys.exit(main())
