# -*- coding: utf-8 -*-
"""Догенерация: (1) кадр приёмной с явно ПУСТОЙ стеной (без единой надписи),
   (2) пустой фон-кабинет 16:9 без людей и без текста."""
import os, gen, pv

HERE = os.path.dirname(os.path.abspath(gen.__file__))
REF = os.path.join(HERE, "refs", "kate_master.png")
MODEL = "flux-2"
STYLE = gen.STYLE
CHAR = ("женщина 68 лет, короткие седые ВЬЮЩИЕСЯ волосы до подбородка, яркие голубые глаза, "
        "мягкое доброе лицо с лёгкими морщинками, спокойная тёплая полуулыбка, синий рабочий "
        "комбинезон на лямках поверх светлой рубашки. ")

JOBS = [
    ("reception_fix2", "3:4", True,
     "Кадр визуальной новеллы: Екатерина Ивановна стоит в скромном кабинете приёмной комиссии, "
     "прижимает к груди папку с документами, спокойна и приветлива. Фон нарочито простой: "
     "письменный стол, шкаф с папками, окно с дневным светом. СТЕНЫ ПОЛНОСТЬЮ ПУСТЫЕ — ни одной "
     "таблички, вывески, плаката и надписи (никакого текста вообще). Полный рост по колено. " + CHAR +
     "Сохрани ЛИЦО, причёску и манеру рисования точно как на прикреплённом образце."),
    ("office_clean", "16:9", False,
     "Фон-локация визуальной новеллы (пустой, без людей): кабинет приёмной комиссии советского "
     "космического центра. Письменный стол со стопкой папок, стул, шкаф с документами, "
     "окно с мягким утренним светом, слева дверь. СТЕНЫ ПОЛНОСТЬЮ ПУСТЫЕ — ни одной таблички, "
     "вывески и надписи, никакого текста. Мягкий аниме-стиль гальгэ, пастель, чистый лайн-арт."),
]


def render(name, ar, with_ref, prompt):
    opts = {"aspect_ratio": ar, "resolution": "1K"}
    if with_ref:
        opts["image_base64"] = gen.b64(REF)
    full = prompt + "\n\nСТИЛЬ: " + STYLE
    try:
        q = pv.price(MODEL, full, opts)
        print(f"[quote] {name:16s} {q.get('priceRub')} ₽", flush=True)
        files, st = pv.generate_to_files(MODEL, full, opts, outdir="assets/gen",
                                         name=f"ok_{name}", max_price_rub=12)
        print(f"[OK] {name:16s} {st.get('priceRub')} ₽ -> {os.path.relpath(files[0], HERE)}", flush=True)
    except Exception as e:
        print(f"[FAIL] {name:16s} {str(e)[:200]}", flush=True)


for name, ar, wr, prompt in JOBS:
    render(name, ar, wr, prompt)
print("DONE", flush=True)
