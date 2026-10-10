# -*- coding: utf-8 -*-
"""ГЛАВНЫЙ ТЕСТ: держит ли nano-banana ОДНОГО персонажа в РАЗНЫХ сценах.
Референс — утверждённая Екатерина. Три новые сцены. Сравниваем nano-banana-2 и -2.1.
"""
import os, gen, pv

HERE = os.path.dirname(os.path.abspath(gen.__file__))
REF = os.path.join(HERE, "assets", "gen", "kate_overalls_0.png")  # утверждённый кадр

BASE = (
    "Тот же персонаж, что на прикреплённом образце: пожилая женщина 68 лет, короткие "
    "седые вьющиеся волосы, яркие голубые глаза, мягкое доброе лицо с лёгкими морщинками, "
    "спокойная тёплая полуулыбка, синий рабочий комбинезон на лямках поверх светлой рубашки. "
    "Сохрани ЛИЦО, причёску и манеру рисования как на образце. Стиль аниме-визуальной новеллы, "
    "cel-shading, чистый лайн-арт, пастель. "
)

SCENES = {
    "s1_reception": "Сцена: стоит в кабинете приёмной комиссии, держит папку с документами, по пояс, спокойна.",
    "s2_window":    "Сцена: у окна, смотрит вдаль, задумчива, лёгкий профиль 3/4, по пояс.",
    "s3_chair":     "Сцена: сидит в кресле, слегка наклонившись вперёд, доверчиво улыбается.",
}

MODELS = {"nanobanana2": "nano-banana-2", "nanobanana21": "nano-banana-2.1"}

for tag, model in MODELS.items():
    for sn, sk in SCENES.items():
        prompt = sk + " " + BASE
        opts = {"aspect_ratio": "3:4", "resolution": "1K", "image_base64": gen.b64(REF)}
        try:
            q = pv.price(model, prompt, opts)
            files, st = pv.generate_to_files(model, prompt, opts, outdir="assets/gen",
                                             name=f"consist_{tag}__{sn}", max_price_rub=12)
            print(f"[OK] {model:16s} {sn:14s} {st.get('priceRub')} ₽ -> {os.path.relpath(files[0], HERE)}")
        except Exception as e:
            print(f"[FAIL] {model:16s} {sn:14s} {str(e)[:150]}")
