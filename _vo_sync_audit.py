# -*- coding: utf-8 -*-
"""Аудит соответствия озвучки тексту: ищем файлы, чей звук не принадлежит
странице (каскад копий при переиспользовании).

Метод: для каждой страницы берём md5 файла; если один и тот же файл стоит на
страницах с разным текстом — это гарантированно ошибка. Дополнительно сверяем
манифест: price==0 + reused_from ==> файл скопирован, а не сгенерирован.
"""
import os, json, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
VD = os.path.join(HERE, 'vn2', 'audio', 'vo')
man = json.load(open(os.path.join(VD, '_voices.json'), encoding='utf-8'))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))


def md5(p):
    with open(p, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


for nid in ['reception']:
    nd = [n for n in D['nodes'] if n.get('id') == nid][0]
    by_hash, reused, total = {}, [], 0
    for i, pg in enumerate(nd['pages']):
        vo = pg.get('vo')
        if not vo:
            continue
        p = os.path.join(VD, os.path.basename(vo))
        h = md5(p) if os.path.exists(p) else 'MISSING'
        by_hash.setdefault(h, []).append(i)
        rec = man.get(vo, {})
        if rec.get('price') == 0 or rec.get('reused_from'):
            reused.append((i, os.path.basename(vo), rec.get('voice'),
                           rec.get('reused_from'), len(rec.get('text') or '')))
        total += len(rec.get('text') or '')
    print('=== %s: страниц %d, символов в манифесте %d' % (nid, len(nd['pages']), total))
    print('-- копии (price=0/reused_from): %d' % len(reused))
    for r in reused:
        print('   стр.%2d %-12s %-10s <- %-12s %4d зн' % r)
    print('-- одинаковый звук на разных страницах:')
    for h, pages in by_hash.items():
        if len(pages) > 1:
            same = len({nd['pages'][i].get('vo') for i in pages}) == 1
            print('   %s: страницы %s%s' % (h[:8], pages,
                                            '' if same else '  <<< РАЗНЫЕ ФАЙЛЫ, ОДИН ЗВУК'))
