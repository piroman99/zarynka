#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сверка озвучки и текста: для каждой страницы VN берём vo-файл,
сравниваем текст страницы с текстом, который реально был озвучен
(поле text в манифесте _voices.json), и проверяем наличие файла.
Печатает расхождения: MISSING / NO_TEXT / DIFF.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
VN2 = os.path.join(ROOT, 'vn2')
VO = os.path.join(VN2, 'audio', 'vo')
MAN = os.path.join(VO, '_voices.json')


def norm(t):
    t = t.replace('«', '"').replace('»', '"').replace('—', '-').replace('–', '-')
    t = t.replace('…', '...')
    t = re.sub(r'[^0-9A-Za-zА-Яа-яЁё]+', ' ', t)
    return re.sub(r'\s+', ' ', t).strip().lower()


def load_content():
    src = open(os.path.join(VN2, 'content.js'), encoding='utf-8').read()
    i = src.index('{')
    j = src.rindex('}')
    return json.loads(src[i:j + 1])


def pages_of(content):
    out = []
    for n in content['nodes']:
        for k, pg in enumerate(n.get('pages') or []):
            if pg.get('vo'):
                out.append((n.get('id') or n.get('t'), k, pg))
    return out


def main():
    content = load_content()
    man = json.load(open(MAN, encoding='utf-8'))
    pages = pages_of(content)
    missing, diff, notext, ok = [], [], [], 0
    for nid, k, pg in pages:
        vo = pg['vo']
        path = os.path.join(VN2, vo)
        if not os.path.exists(path):
            missing.append((nid, k, vo, pg['tx'][:60]))
            continue
        m = man.get(vo) or {}
        txt = m.get('text')
        if not txt:
            notext.append((nid, k, vo, pg['tx'][:60], m.get('voice')))
            continue
        a, b = norm(txt), norm(pg['tx'])
        if a != b:
            diff.append((nid, k, vo, pg['tx'], txt))
        else:
            ok += 1
    print('страниц с vo: %d | совпало: %d | нет файла: %d | нет текста в манифесте: %d | РАСХОЖДЕНИЙ: %d'
          % (len(pages), ok, len(missing), len(notext), len(diff)))
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
    from collections import Counter
    c = Counter(pg['vo'] for _, _, pg in pages)
    dup = {v: n for v, n in c.items() if n > 1}
    if dup:
        print('\n-- один файл на несколько страниц --')
        for v, n in dup.items():
            print('  %s x%d' % (v, n))
    return 1 if (missing or diff) else 0


if __name__ == '__main__':
    sys.exit(main())
