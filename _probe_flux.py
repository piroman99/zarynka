# -*- coding: utf-8 -*-
"""Что умеют flux-2 / nano-banana-2: вход картинки, параметры, цена."""
import json, pv

for m in ("flux-2", "flux-2-max", "nano-banana-2", "nano-banana-2.1", "grok-imagine"):
    try:
        c = pv.capabilities(m)
        print("=" * 70)
        print(m, "->", json.dumps(c, ensure_ascii=False)[:1500])
    except Exception as e:
        print(m, "ERR", e)
