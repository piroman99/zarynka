# -*- coding: utf-8 -*-
"""Индекс узла в content.js по его id ('reception', 'p6', 's1' …).

Индексы узлов СДВИГАЮТСЯ при вставке кадров (так уже было при добавлении посвящения,
так случилось при вставке кадра p6) — тесты не должны держать номер числом.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def data():
    src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
    return json.loads(src[src.index('=') + 1:].strip().rstrip(';'))


def node_index(nid):
    for i, nd in enumerate(data()['nodes']):
        if nd.get('id') == nid or nd.get('t') == nid:
            return i
    raise KeyError('нет узла %r в content.js' % nid)


if __name__ == '__main__':
    for i, nd in enumerate(data()['nodes']):
        print('%2d  %-9s %-10s стр=%d' % (i, nd.get('t'), nd.get('id') or '', len(nd.get('pages') or [])))
