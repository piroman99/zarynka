# -*- coding: utf-8 -*-
"""Рейтинг генераторов картинок: ОДИН промпт → результат + ценник + время.

Запуск:  python3 rating.py [модель ...]   (без аргументов — весь шортлист)
"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pv

PROMPT = (
    "Аниме-иллюстрация в стиле японской визуальной новеллы (гальгэ, cel-shading, "
    "чистый выразительный лайн-арт, мягкая пастельная палитра): поясной портрет "
    "женщины-космонавта 68 лет — короткие седые вьющиеся волосы, яркие голубые глаза, "
    "мягкое доброе лицо в лёгких морщинках, спокойная тёплая полуулыбка; оранжево-белый "
    "космический скафандр с высоким воротом и круглым знаком с птицей на груди. "
    "Смотрит прямо на зрителя, ровный однотонный светлый фон."
)

# модель -> opts (aspect/resolution только если поддерживаются)
SHORTLIST = [
    ("z-image",            {"aspect_ratio": "3:4"}),
    ("gpt-image-2",        {"aspect_ratio": "3:4", "resolution": "1K"}),
    ("nano-banana-2",      {"aspect_ratio": "3:4", "resolution": "1K"}),
    ("seedream-5-0-flash", {"aspect_ratio": "3:4", "resolution": "1K"}),
    ("grok-imagine",       {"aspect_ratio": "3:4"}),
    ("imagen4",            {"aspect_ratio": "3:4"}),
    ("qwen3-image",        {"aspect_ratio": "3:4", "resolution": "1K"}),
    ("flux-2",             {"aspect_ratio": "3:4", "resolution": "1K"}),
    ("seedream-5-0-pro",   {"resolution": "1K"}),
    ("recraft-v4-1",       {"aspect_ratio": "3:4"}),
    ("flux-2-max",         {"aspect_ratio": "3:4", "resolution": "1MP"}),
    ("nano-banana-pro",    {"aspect_ratio": "3:4", "resolution": "1K"}),
]

OUT = os.path.join(HERE, "assets", "rating")


def slug(m):
    return m.replace(".", "-").replace("/", "-")


def main(models=None):
    os.makedirs(OUT, exist_ok=True)
    report_path = os.path.join(OUT, "report.json")
    report = json.load(open(report_path, encoding="utf-8")) if os.path.exists(report_path) else {}
    todo = [(m, o) for m, o in SHORTLIST if not models or m in models]
    for m, opts in todo:
        t0 = time.time()
        rec = {"model": m, "opts": opts}
        try:
            q = pv.price(m, PROMPT, opts)
            rec["quote_rub"] = q.get("priceRub")
        except Exception as e:
            rec["quote_rub"] = None; rec["quote_err"] = str(e)[:200]
        try:
            files, st = pv.generate_to_files(m, PROMPT, opts, outdir="assets/rating",
                                             name=slug(m), max_price_rub=20)
            rec["ok"] = True
            rec["price_rub"] = st.get("priceRub")
            rec["seconds"] = round(time.time() - t0, 1)
            rec["file"] = os.path.relpath(files[0], HERE) if files else None
        except Exception as e:
            rec["ok"] = False
            rec["seconds"] = round(time.time() - t0, 1)
            rec["error"] = str(e)[:300]
        report[m] = rec
        json.dump(report, open(report_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"[rating] {m:22s} ok={rec.get('ok')} price={rec.get('price_rub')} "
              f"t={rec.get('seconds')}s {rec.get('error','')}")
    print("DONE")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
