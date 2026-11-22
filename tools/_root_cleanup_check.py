# -*- coding: utf-8 -*-
"""Проверка перед уборкой: критичные скрипты должны попасть в «живые»."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import _root_cleanup as rc  # noqa: E402
import re  # noqa: E402

root_scripts = sorted(f for f in os.listdir(HERE)
                      if os.path.isfile(os.path.join(HERE, f))
                      and f.endswith(('.py', '.sh'))
                      and not f.startswith(('_root_cleanup', '_move_tools',
                                            '_fix_tools_paths', '_stage_alley',
                                            '_call_graph', '_refs_scan')))
seeds = set()
for p, txt in rc.repo_texts():
    for tok in rc.TOKEN.findall(txt):
        if tok in root_scripts:
            seeds.add(tok)
graph = {}
for name in root_scripts:
    with open(os.path.join(HERE, name), encoding='utf-8', errors='ignore') as fh:
        txt = fh.read()
    graph[name] = {t for t in rc.TOKEN.findall(txt) if t in root_scripts and t != name}
live = set(seeds)
stack = list(seeds)
while stack:
    cur = stack.pop()
    for nxt in graph.get(cur, ()):
        if nxt not in live:
            live.add(nxt)
            stack.append(nxt)

CRIT = ['_vn2_build.py', '_vn2_nodes.py', '_vn2_mem.py', '_vn2_toc.py', 'pv.py',
        '_cdp.py', '_pl_regress.py', '_vn2_script.py', 'vk.py', 'tg.py',
        '_poet_matte.py', '_bench_compose2.py', '_gh_push.py', '_pl_verify2.py']
print('живых: %d, мёртвых: %d из %d' % (len(live), len(root_scripts) - len(live),
                                        len(root_scripts)))
print('\nкритичные:')
for c in CRIT:
    if not os.path.exists(os.path.join(HERE, c)):
        print('  %-24s НЕТ ФАЙЛА' % c)
        continue
    print('  %-24s %s' % (c, 'живой' if c in live else '!!! МЁРТВЫЙ'))
