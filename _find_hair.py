# -*- coding: utf-8 -*-
"""Ищет в тексте любые описания причёски Екатерины: вьющ/волнист/кудр/сед/локон и т.п."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
txt = open(os.path.join(HERE, "assets", "story.txt"), encoding="utf-8").read()
paras = [x.strip() for x in txt.split("\n") if x.strip()]
KEYS = ["вьющ", "вьют", "волнист", "кудр", "кучер", "локон", "сед", "волос", "причёс",
        "причес", "стрижк", "ежик", "ёжик", "хвост", "коса", "прям"]
for i, p in enumerate(paras):
    low = p.lower()
    hits = sorted({k for k in KEYS if k in low})
    if hits:
        print(f"#{i} {hits}\n   {p[:400]}\n")
