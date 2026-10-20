# -*- coding: utf-8 -*-
"""Сверка пролога: текст страниц пролога в текущей сборке против сборки,
которой озвучивались файлы (коммит c98e4e7). Если тексты совпали — озвучка
пролога соответствует страницам."""
import json
import subprocess

HERE = '/home/ivan/.nanobot/workspace/novella/zaryanka'


def load(rev):
    src = subprocess.run(['git', 'show', '%s:vn2/content.js' % rev], cwd=HERE,
                         capture_output=True, text=True).stdout
    return json.loads(src[src.index('=') + 1:].strip().rstrip(';'))


def prolog(D):
    out = {}
    for n in D['nodes']:
        nid = n.get('id')
        if nid and nid.startswith('s') and nid[1:].isdigit():
            for k, pg in enumerate(n.get('pages') or []):
                out[pg.get('vo')] = pg['tx']
    return out


cur = prolog(load('HEAD'))
old = prolog(load('c98e4e7'))
print('файлов: сейчас %d, при озвучке %d' % (len(cur), len(old)))
for vo in sorted(set(cur) | set(old)):
    a, b = cur.get(vo), old.get(vo)
    if a == b:
        print('OK   %s' % vo)
    else:
        print('DIFF %s' % vo)
        print('   сейчас : %s' % (a or '-')[:120])
        print('   озвучено: %s' % (b or '-')[:120])
