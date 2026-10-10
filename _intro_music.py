# -*- coding: utf-8 -*-
"""Музыкальная тема для интро «Зарянки» — 2 варианта настроения."""
import os, gen, pv

HERE = os.path.dirname(os.path.abspath(gen.__file__))

THEMES = {
    "theme_warm": {
        "prompt": ("Тёплый ностальгический оркестровый саундтрек для аниме-визуальной новеллы "
                   "о космосе, мечте и надежде. Фортепиано, струнные, мягкие синтезаторы, "
                   "нежные колокольчики. Медленное светлое нарастание, немного светлой грусти, "
                   "финал — с верой в будущее. Без резких ударных."),
        "style": "cinematic orchestral, warm, nostalgic, anime soundtrack",
    },
    "theme_epic": {
        "prompt": ("Эпично-лирическая тема для трейлера аниме-новеллы о женщине-космонавте, "
                   "которая летит к Марсу. Медленное вступление на фортепиано, затем широкие "
                   "струнные и хор, нарастание к светлому торжественному финалу. Надежда, "
                   "величие, тихая сила."),
        "style": "epic orchestral trailer, emotional, hopeful, cinematic",
    },
}

for name, t in THEMES.items():
    opts = {"instrumental": True, "style": t["style"], "title": name,
            "duration": 30, "version": "v6"}
    try:
        q = pv.price("suno", t["prompt"], opts)
        print(f"[quote] {name} {q.get('priceRub')} ₽", flush=True)
        files, st = pv.generate_to_files("suno", t["prompt"], opts, outdir="assets/audio",
                                         name=name, max_price_rub=12)
        print(f"[OK] {name} {st.get('priceRub')} ₽ -> {os.path.relpath(files[0], HERE)}", flush=True)
    except Exception as e:
        print(f"[FAIL] {name} {str(e)[:200]}", flush=True)
print("MUSIC DONE", flush=True)
