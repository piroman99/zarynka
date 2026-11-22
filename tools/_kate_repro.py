# -*- coding: utf-8 -*-
"""Может ли flux-2 ПОВТОРИТЬ уже утверждённую Екатерину (image-to-image с эталоном)?"""
import os, gen, pv

HERE = os.path.dirname(os.path.abspath(gen.__file__))
REF = os.path.join(HERE, "assets", "gen", "kate_overalls_0.png")   # утверждённый кадр (gpt-image-2)

PROMPT = (
    "Воспроизведи ТОЧНО того же персонажа, что и на прикреплённом образце — пожилая женщина "
    "68 лет, короткие седые вьющиеся волосы, яркие голубые глаза, добрые морщинки, спокойная "
    "тёплая полуулыбка, синий рабочий комбинезон на лямках поверх светлой рубашки. "
    "Сохрани лицо, причёску, одежду, позу и манеру рисования как на образце. "
    "Поясной спрайт визуальной новеллы, ровный однотонный светло-серый фон.\n\nСТИЛЬ: " + gen.STYLE
)

for model, extra in (("flux-2", {}),
                     ("nano-banana-2.1", {"resolution": "1K"}),
                     ("grok-imagine", {})):
    opts = {"aspect_ratio": "3:4", "image_base64": gen.b64(REF)}
    opts.update(extra)
    q = pv.price(model, PROMPT, opts)
    print(f"[{model}] quote={q.get('priceRub')} ₽")
    try:
        files, st = pv.generate_to_files(model, PROMPT, opts, outdir="assets/gen",
                                         name=f"kate_repro__{model}", max_price_rub=12)
        print(f"  -> {os.path.relpath(files[0], HERE)} price={st.get('priceRub')}")
    except Exception as e:
        print("  FAIL", str(e)[:200])
