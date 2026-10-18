# -*- coding: utf-8 -*-
"""Сколько встанет: реальные котировки PlusVibe на нужные кадры/клипы (без генерации)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

print('баланс:', pv.balance())
prompt = ("акварельная иллюстрация в стиле советской кинохроники: женщина 68 лет, "
          "седые вьющиеся волосы, синий рабочий комбинезон, держит папку, "
          "у окна приёмной комиссии")
cases = [
    ('flux-2  16:9 (pro)', 'flux-2', {'aspect_ratio': '16:9'}),
    ('flux-2  16:9 (pro, 2K)', 'flux-2', {'aspect_ratio': '16:9', 'resolution': '2K'}),
    ('flux-2  3:4 (pro)', 'flux-2', {'aspect_ratio': '3:4'}),
    ('nano-banana-2.1 16:9', 'nano-banana-2.1', {'aspect_ratio': '16:9'}),
    ('gpt-image-2 16:9', 'gpt-image-2', {'aspect_ratio': '16:9'}),
]
for label, model, opts in cases:
    try:
        q = pv.price(model, prompt, opts)
        print('%-24s %s ₽  %s' % (label, q.get('priceRub'), json.dumps(q.get('raw') or q, ensure_ascii=False)[:120]))
    except Exception as e:
        print('%-24s ERR %s' % (label, str(e)[:160]))

# i2v за секунду
for label, model, opts in [
    ('MiniMax-Hailuo-02 5s 768P', 'MiniMax-Hailuo-02', {'duration': 5, 'resolution': '768P'}),
]:
    try:
        q = pv.price(model, 'оживить кадр', opts)
        print('%-24s %s ₽' % (label, q.get('priceRub')))
    except Exception as e:
        print('%-24s ERR %s' % (label, str(e)[:160]))
