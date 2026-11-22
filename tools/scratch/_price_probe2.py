# -*- coding: utf-8 -*-
"""Цены i2v: MiniMax-Hailuo-02 (duration — СТРОКА) и Kling (если найду id)."""
import os, json, gen, pv

HERE = os.path.dirname(os.path.abspath(gen.__file__))
ship = os.path.join(HERE, "assets/gen/ok_space_ship_0.jpg")
img = gen.b64(ship)

for res in ("512P", "768P", "1080P"):
    for dur in ("5", "10"):
        try:
            q = pv.price("MiniMax-Hailuo-02", "лёгкий дрейф, движение камеры",
                         {"duration": dur, "resolution": res, "image_base64": img})
            print(f"MiniMax-Hailuo-02 {res} {dur}s -> {q.get('priceRub')} ₽")
        except Exception as e:
            print(f"MiniMax-Hailuo-02 {res} {dur}s ERR {str(e)[:140]}")

# поищем kling/др. видео-модели в каталоге
try:
    d = pv.models("video")
    ids = sorted({m.get("id") for m in d.get("data", []) if m.get("id")})
    print("\nVIDEO IDS:", [i for i in ids if i][:40])
except Exception as e:
    print("catalog err", str(e)[:200])
