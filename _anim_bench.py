# -*- coding: utf-8 -*-
"""Замер: сколько стоит кадр каждого типа (P0 3D / мок) — чтобы понять, почему сборка долгая."""
import os, time, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# выполним модуль до стадии рендера (обрежем на "---- 1) немое видео")
src = open(os.path.join(HERE, '_prolog_animatic.py')).read()
head = src.split('# ---- 1) немое видео')[0]
ns = {'__file__': os.path.join(HERE, '_prolog_animatic.py'), '__name__': '__probe__'}
exec(compile(head, '_prolog_animatic.py', 'exec'), ns)

render_shot = ns['render_shot']
segs = ns['segs']

print('сегменты:')
for nm, a, dd in segs:
    print('  %-3s %.2f -> %.2f (%.2f c)' % (nm, a, a + dd, dd))

def bench(nm, lt, dur, n=6):
    t0 = time.time()
    for _ in range(n):
        render_shot(nm, lt, dur)
    dt = (time.time() - t0) / n
    print('  %-3s  %.3f с/кадр  -> всего ~%.0f с' % (nm, dt, dt * dur * 25))
    return dt * dur * 25

tot = 0.0
for nm, a, dd in segs:
    lt = dd * 0.5
    tot += bench(nm, lt, dd)
print('ОЦЕНКА немого видео: ~%.0f с (%.1f мин)' % (tot, tot / 60))
