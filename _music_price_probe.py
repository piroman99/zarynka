# -*- coding: utf-8 -*-
"""Проверка цен на музыку БЕЗ генерации (подобрать в бюджет ~25 ₽)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

STYLE = ("warm nostalgic instrumental, Soviet retro flavor, acoustic piano and guitar, "
         "calm mid tempo, no vocals")
combos = [
    ("suno", {"version": "v6",      "instrumental": True, "duration": 80}),
    ("suno", {"version": "v6",      "instrumental": True, "duration": 30}),
    ("suno", {"version": "v6",      "instrumental": True, "duration": 60}),
    ("suno", {"version": "v6-mini", "instrumental": True, "duration": 80}),
    ("suno", {"version": "v6-mini", "instrumental": True, "duration": 30}),
    ("suno", {"version": "v6-wild", "instrumental": True, "duration": 80}),
    ("lyria-3-5", {"instrumental": True, "bpm": 92}),
    ("lyria-3-5", {}),
]
for m, o in combos:
    try:
        q = pv.price(m, STYLE, o)
        print(f"{m:12s} {str(o)[:60]:60s} -> {q.get('priceRub')} ₽")
    except Exception as e:
        print(f"{m:12s} {str(o)[:60]:60s} -> ERROR {e}")
