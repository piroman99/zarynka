# -*- coding: utf-8 -*-
"""Доснять последний кадр согласованности (nano-banana-2.1, s3_chair)."""
import os, gen, pv

HERE = os.path.dirname(os.path.abspath(gen.__file__))
REF = os.path.join(HERE, "assets", "gen", "kate_overalls_0.png")
BASE = (
    "Тот же персонаж, что на прикреплённом образце: пожилая женщина 68 лет, короткие "
    "седые вьющиеся волосы, яркие голубые глаза, мягкое доброе лицо с лёгкими морщинками, "
    "спокойная тёплая полуулыбка, синий рабочий комбинезон на лямках поверх светлой рубашки. "
    "Сохрани ЛИЦО, причёску и манеру рисования как на образце. Стиль аниме-визуальной новеллы, "
    "cel-shading, чистый лайн-арт, пастель. "
)
scene = "Сцена: сидит в кресле, слегка наклонившись вперёд, доверчиво улыбается."
prompt = scene + " " + BASE
opts = {"aspect_ratio": "3:4", "resolution": "1K", "image_base64": gen.b64(REF)}
print("start", flush=True)
files, st = pv.generate_to_files("nano-banana-2.1", prompt, opts, outdir="assets/gen",
                                 name="consist_nanobanana21__s3_chair", max_price_rub=12)
print("DONE", files, st.get("priceRub"), flush=True)
