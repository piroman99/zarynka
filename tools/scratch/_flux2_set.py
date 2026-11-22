# -*- coding: utf-8 -*-
"""Ключевые кадры через flux-2 (выбранный заказчиком стиль) + вариант «попроще»."""
import os, gen, pv

HERE = os.path.dirname(os.path.abspath(gen.__file__))
SPR = os.path.join(HERE, "assets", "orig", "za smile.png")

JOBS = [
    # name,                  scene,            ref, simple
    ("flux2_zaryanka",        "zaryanka_ref",   SPR, False),
    ("flux2_zaryanka_simple", "zaryanka_ref",   SPR, True),
    ("flux2_kate",            "kate_overalls",  SPR, False),
    ("flux2_bg_reception",    "bg_reception_vn", None, False),
]

for name, scene, ref, simple in JOBS:
    spec = gen.SCENES[scene]
    style = gen.STYLE_SIMPLE if simple else gen.STYLE
    prompt = spec["prompt"] + "\n\nСТИЛЬ: " + style
    opts = {"aspect_ratio": spec.get("aspect", "3:4"), "resolution": spec.get("res", "1K")}
    if ref and os.path.exists(ref):
        opts["image_base64"] = gen.b64(ref)
    q = pv.price("flux-2", prompt, opts)
    print(f"[{name}] quote={q.get('priceRub')} ₽  ref={'yes' if ref else 'no'}")
    files, st = pv.generate_to_files("flux-2", prompt, opts, outdir="assets/gen",
                                     name=name, max_price_rub=12)
    print(f"  -> {os.path.relpath(files[0], HERE)}  price={st.get('priceRub')}")
