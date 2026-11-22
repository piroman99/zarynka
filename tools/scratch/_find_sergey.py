# -*- coding: utf-8 -*-
"""Всё, что текст говорит о Сергее/Лихнецком — внешность, должность, характер."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
paras = [x.strip() for x in open(os.path.join(ROOT, "assets", "story.txt"), encoding="utf-8").read().split("\n") if x.strip()]

KEYS = ["лихнецк", "сергей", "серёж", "серёг", " сережа", "серге", "лейтенант", "капитан",
        "майор", "полковн", "инженер", "учен", "учён", "сотрудник", "форма", "мундир",
        "бород", "щетин", "небрит", "усы", "выглядит", "уставш", "устал", "сонн", "невысп",
        "мятая", "мятый", "неряшл", "растрёп", "растреп", "рубашк", "комбинезон", "кепк", "фуражк"]

for i, p in enumerate(paras):
    low = " " + p.lower()
    hits = sorted({k for k in KEYS if k in low})
    if hits:
        print(f"#{i} {hits}\n   {p[:600]}\n")
