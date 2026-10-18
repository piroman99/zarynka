# -*- coding: utf-8 -*-
"""Баланс PlusVibe + цена flux-2 16:9 (смета по S6)."""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

print('balance:', json.dumps(pv.balance(), ensure_ascii=False))
for model in ('flux-2', 'nano-banana-2.1'):
    for res in ('1K', '2K'):
        try:
            st = pv.price(model, 'test prompt for pricing', {'aspect_ratio': '16:9', 'resolution': res})
            print(model, res, json.dumps(st, ensure_ascii=False)[:220])
        except Exception as e:
            print(model, res, 'err:', str(e)[:200])
