# -*- coding: utf-8 -*-
"""Собирает лист-рейтинг генераторов с подписями из assets/rating/report.json."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import review_sheet as RS

OUT = os.path.join(HERE, "assets", "rating")
rep = json.load(open(os.path.join(OUT, "report.json"), encoding="utf-8"))

rows = sorted(rep.values(), key=lambda r: (r.get("price_rub") or r.get("quote_rub") or 999))
items = []
for r in rows:
    price = r.get("price_rub")
    base = r["model"]
    if r.get("file") and os.path.exists(os.path.join(HERE, r["file"])):
        label = f"{base} · {price if price is not None else '?'} ₽ · {r.get('seconds','?')}с"
        items.append((label, os.path.join(HERE, r["file"])))
    else:
        items.append((f"{base} · ОШИБКА", None))

RS.sheet(items, os.path.join(OUT, "rating_sheet.png"),
         cols=4, cell=(430, 520), title="Зарянка — рейтинг генераторов (один промпт, портрет)")

# краткая таблица в текст
print(f"{'model':22s} {'price':>7s} {'sec':>6s}  ok")
for r in rows:
    print(f"{r['model']:22s} {str(r.get('price_rub')):>7s} {str(r.get('seconds')):>6s}  {r.get('ok')}")
tot = sum((r.get('price_rub') or 0) for r in rows)
print(f"{'ИТОГО':22s} {tot:>7.2f} ₽")
