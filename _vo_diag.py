# -*- coding: utf-8 -*-
"""Диагностика озвучки: какие страницы получают голос персонажа, хотя текст авторский."""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.join(HERE, "assets", "story.txt")

lines = open(STORY, encoding="utf-8").read().split("\n")
L = {i + 1: ln.strip() for i, ln in enumerate(lines)}

reception_par = {n: L[n] for n in range(13, 68) if L.get(n) and not L[n].startswith("*")}

SPEAK = {15: "Старик", 23: "Сергей", 25: "Екатерина", 29: "Сергей", 31: "Екатерина",
         33: "Сергей", 37: "Сергей", 41: "Сергей", 43: "Екатерина", 45: "Сергей",
         47: "Екатерина", 49: "Сергей", 51: "Екатерина", 53: "Сергей", 57: "Сергей",
         61: "Сергей", 63: "Екатерина", 65: "Сергей", 67: "Екатерина"}
NARR_OVERRIDE = {11, 12, 25}

SENT = re.compile(r"(?<=[.!?…])\s+(?=[А-ЯA-Z«—])")


def pages(text, maxn=2):
    parts = [s.strip() for s in SENT.split(text) if s.strip()]
    out, cur = [], []
    for s in parts:
        cur.append(s)
        if len(cur) >= maxn:
            out.append(" ".join(cur)); cur = []
    if cur:
        out.append(" ".join(cur))
    return out


idx = 0
for n in sorted(reception_par):
    who = SPEAK.get(n, "")
    pgs = pages(reception_par[n], 2)
    for k, p in enumerate(pgs):
        voiced = who if (who and idx not in NARR_OVERRIDE) else ""
        dash = p.lstrip().startswith("—")
        mark = ""
        if voiced and not dash:
            mark = "  <<< ПЕРСОНАЖ БЕЗ ТИРЕ"
        if (not voiced) and dash:
            mark = "  <<< ТИРЕ БЕЗ ПЕРСОНАЖА"
        print("%2d стр.%2d абз.%2d %-11s %s %s%s"
              % (idx, n, k, voiced or "-", "«—»" if dash else "авт", p[:70].replace("\n", " "), mark))
        idx += 1
