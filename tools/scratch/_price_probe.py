# -*- coding: utf-8 -*-
"""Проверка баланса и цен: nano-banana-2.1 (кадры) и MiniMax-Hailuo-02 (оживление кадров)."""
import os, json, gen, pv

HERE = os.path.dirname(os.path.abspath(gen.__file__))
REF = os.path.join(HERE, "refs", "kate_master.png")
ship = os.path.join(HERE, "assets/gen/ok_space_ship_0.jpg")

print("=== BALANCE ===")
print(json.dumps(pv.balance(), ensure_ascii=False))

print("\n=== IMAGE: nano-banana-2.1 (3:4, t2i) ===")
print(pv.price("nano-banana-2.1", "тест", {"aspect_ratio": "3:4", "resolution": "1K"}))

print("\n=== IMAGE: nano-banana-2.1 (3:4, i2i c референсом) ===")
print(pv.price("nano-banana-2.1", "тест", {"aspect_ratio": "3:4", "resolution": "1K",
                                           "image_base64": gen.b64(REF)}))

for res in ("512P", "768P", "1080P"):
    print(f"\n=== VIDEO: MiniMax-Hailuo-02 5s {res} (i2v) ===")
    try:
        print(pv.price("MiniMax-Hailuo-02", "лёгкое движение камеры",
                       {"duration": 5, "resolution": res, "image_base64": gen.b64(ship)}))
    except Exception as e:
        print("ERR", str(e)[:200])
