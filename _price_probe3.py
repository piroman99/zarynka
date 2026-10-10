# -*- coding: utf-8 -*-
"""Изолируем причину: t2v без картинки, i2v с image_url, разные модели видео-каталога."""
import os, gen, pv

HERE = os.path.dirname(os.path.abspath(gen.__file__))
ship = os.path.join(HERE, "assets/gen/ok_space_ship_0.jpg")
img = gen.b64(ship)

def t(label, model, opts):
    try:
        q = pv.price(model, "тест", opts)
        print(f"{label:55s} -> {q.get('priceRub')} ₽")
    except Exception as e:
        msg = str(e)
        msg = msg.split('"message":"')[1].split('"')[0] if '"message":"' in msg else msg[:120]
        print(f"{label:55s} ERR {msg}")

print("--- MiniMax-Hailuo-02 ---")
t("t2v 768P 5s (без картинки)", "MiniMax-Hailuo-02", {"duration": "5", "resolution": "768P"})
t("i2v 768P 5s (image_base64)", "MiniMax-Hailuo-02", {"duration": "5", "resolution": "768P", "image_base64": img})
t("i2v 512P 5s (image_base64)", "MiniMax-Hailuo-02", {"duration": "5", "resolution": "512P", "image_base64": img})
t("i2v 768P 5s (image_url)", "MiniMax-Hailuo-02",
  {"duration": "5", "resolution": "768P", "image_url": "https://plusvibeapi.ru/x.jpg"})

print("\n--- какие вообще видео-модели в каталоге (kind=video) ---")
d = pv.models("video")
seen = []
for m in d.get("data", []):
    i = m.get("id")
    if i and i not in seen and "tts" not in i and "/" not in i:
        seen.append(i)
print(seen)
