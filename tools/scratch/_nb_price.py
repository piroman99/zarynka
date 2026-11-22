# -*- coding: utf-8 -*-
"""Баланс + цены семейства nano-banana на нашем промпте."""
import json, pv

print("BALANCE:", pv.balance())

PROMPT = (
    "Аниме-иллюстрация в стиле японской визуальной новеллы (гальгэ, cel-shading, "
    "чистый выразительный лайн-арт, мягкая пастельная палитра): поясной портрет "
    "женщины-космонавта 68 лет — короткие седые вьющиеся волосы, яркие голубые глаза, "
    "мягкое доброе лицо в лёгких морщинках, спокойная тёплая полуулыбка; оранжево-белый "
    "космический скафандр с высоким воротом. Смотрит прямо на зрителя, ровный светлый фон."
)

for m, opts in [("nano-banana", {"aspect_ratio": "3:4"}),
                ("nano-banana-2", {"aspect_ratio": "3:4", "resolution": "1K"}),
                ("nano-banana-2.1", {"aspect_ratio": "3:4", "resolution": "1K"}),
                ("nano-banana-pro", {"aspect_ratio": "3:4", "resolution": "1K"})]:
    try:
        q = pv.price(m, PROMPT, opts)
        print(f"{m:20s} {q.get('priceRub')} ₽")
    except Exception as e:
        print(f"{m:20s} ERR {str(e)[:120]}")
