# -*- coding: utf-8 -*-
"""Разовые генерации с точным набором opts (обход ограничений конкретных моделей)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pv, gen

JOBS = {
    "sergey_grok": (
        "grok-imagine",
        gen.SCENES["sergey"]["prompt"] + "\n\nСТИЛЬ: " + gen.STYLE,
        {"aspect_ratio": "3:4", "enable_pro": False},
    ),
}

if __name__ == "__main__":
    names = sys.argv[1:] or list(JOBS)
    for n in names:
        model, prompt, opts = JOBS[n]
        q = pv.price(model, prompt, opts)
        print(f"[{n}] {model} quote={q.get('priceRub')} opts={opts}")
        files, st = pv.generate_to_files(model, prompt, opts, outdir="assets/gen",
                                         name=n, max_price_rub=20)
        print("=>", files, st.get("priceRub"))
