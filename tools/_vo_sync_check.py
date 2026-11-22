#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сверка озвучки и текста: для каждого СЕГМЕНТА страницы VN берём vo-файл,
сравниваем текст сегмента с текстом, который реально был озвучен
(поле text в манифесте _voices.json), и проверяем наличие файла.
Печатает расхождения: MISSING / NO_TEXT / DIFF.
Сегменты: у склеенной страницы их два (реплика + авторская вставка) — см. _vo_util.
"""
import os
import sys
from collections import Counter

import _vo_util as U


def main():
    content = U.load_content()
    man = U.load_manifest()
    segs = U.segments(content)
    missing, diff, notext, ok = [], [], [], 0
    for nid, k, vo, tx, who in segs:
        path = os.path.join(U.VN2, vo)
        if not os.path.exists(path):
            missing.append((nid, k, vo, tx[:60]))
            continue
        m = man.get(vo) or {}
        got = m.get('text')
        if not got:
            notext.append((nid, k, vo, tx[:60], m.get('voice')))
            continue
        if U.norm(got) != U.norm(tx):
            diff.append((nid, k, vo, tx, got))
        else:
            ok += 1
    print('сегментов с vo: %d | совпало: %d | нет файла: %d | нет текста в манифесте: %d | РАСХОЖДЕНИЙ: %d'
          % (len(segs), ok, len(missing), len(notext), len(diff)))
    if missing:
        print('\n-- нет файла --')
        for r in missing:
            print('  %s[%d] %s  | %s' % r)
    if notext:
        print('\n-- манифест без текста --')
        for r in notext:
            print('  %s[%d] %s voice=%s | %s' % r)
    if diff:
        print('\n-- текст не совпадает с озвученным --')
        for nid, k, vo, cur, old in diff:
            print('  %s[%d] %s' % (nid, k, vo))
            print('     сейчас : %s' % cur)
            print('     озвучено: %s' % old)
    # дубли: один и тот же файл на нескольких страницах
    c = Counter(vo for _, _, vo, _, _ in segs)
    dup = {v: n for v, n in c.items() if n > 1}
    if dup:
        print('\n-- один файл на несколько страниц --')
        for v, n in dup.items():
            print('  %s x%d' % (v, n))
    return 1 if (missing or diff) else 0


if __name__ == '__main__':
    sys.exit(main())
