# -*- coding: utf-8 -*-
"""Размеры клиентских картинок сцены «аллея»: спрайты поэта и проп-скамейка."""
import os

VN2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vn2')
for sub in ('img/char', 'img/prop'):
    d = os.path.join(VN2, sub)
    if not os.path.isdir(d):
        print('нет', sub)
        continue
    tot = 0
    for n in sorted(os.listdir(d)):
        if not (n.startswith('poet_seat') or n.startswith('bench')):
            continue
        p = os.path.join(d, n)
        sz = os.path.getsize(p)
        tot += sz
        print('%-28s %6.0f КБ' % (sub + '/' + n, sz / 1024))
    print('  итого %s: %.1f МБ' % (sub, tot / 1048576))
