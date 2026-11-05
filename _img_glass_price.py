# -*- coding: utf-8 -*-
"""Сколько стоит gpt-image-2 в разных пропорциях (цена зависит от кадра)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv  # noqa: E402

P = 'тест'
for ar in ('1:1', '3:2', '4:3', '16:9', '16:10', '21:9', '2:1', '3:4'):
    for res in ('1K', '2K'):
        try:
            q = pv.price('gpt-image-2', P, {'aspect_ratio': ar, 'resolution': res})
            print('%-6s %-3s %8s RUB' % (ar, res, q.get('priceRub')))
        except Exception as e:  # noqa: BLE001
            print('%-6s %-3s ERR %s' % (ar, res, str(e)[:80]))
