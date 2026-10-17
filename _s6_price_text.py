# -*- coding: utf-8 -*-
"""Котировки под S6 на моделях, которые умеют кириллицу (gpt-image-2 и др.). Без генерации."""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

print('баланс:', pv.balance())
prompt = "утро, арка КПП Звёздного городка 2061, очередь людей, вывеска без ошибок"
cases = [
    ('gpt-image-2 16:9', 'gpt-image-2', {'aspect_ratio': '16:9'}),
    ('gpt-image-2 16:9 +2K', 'gpt-image-2', {'aspect_ratio': '16:9', 'resolution': '2K'}),
    ('gpt-image-2-5 16:9', 'gpt-image-2-5', {'aspect_ratio': '16:9'}),
    ('nano-banana-2.1 16:9', 'nano-banana-2.1', {'aspect_ratio': '16:9'}),
    ('nano-banana-pro 16:9', 'nano-banana-pro', {'aspect_ratio': '16:9'}),
    ('ideogram-v4 16:9', 'ideogram-v4', {'aspect_ratio': '16:9'}),
]
for label, model, opts in cases:
    try:
        q = pv.price(model, prompt, opts)
        print('%-22s %s ₽  est=%s' % (label, q.get('priceRub'), q.get('isEstimate')))
    except Exception as e:
        print('%-22s ERR %s' % (label, str(e)[:150]))
