# -*- coding: utf-8 -*-
"""Цены i2v с image_base64 у hailuo-2-3 / seedance-2-0-mini; и upload с purpose."""
import os, json, uuid, urllib.request, gen, pv

HERE = os.path.dirname(os.path.abspath(gen.__file__))
ship = os.path.join(HERE, "assets/gen/ok_space_ship_0.jpg")
img = gen.b64(ship)

def t(label, model, opts):
    try:
        q = pv.price(model, "лёгкий дрейф камеры, оживление кадра", opts)
        print(f"{label:52s} -> {q.get('priceRub')} ₽")
    except Exception as e:
        msg = str(e)
        msg = msg.split('"message":"')[1].split('"')[0] if '"message":"' in msg else msg[:110]
        print(f"{label:52s} ERR {msg}")

print("=== hailuo-2-3 (base64) ===")
for res in (None, "512P", "768P", "1080P"):
    o = {"duration": "5", "image_base64": img}
    if res: o["resolution"] = res
    t(f"hailuo-2-3 5s res={res}", "hailuo-2-3", o)

print("\n=== seedance-2-0-mini (base64) ===")
for res in (None, "480p", "720p", "1080p"):
    o = {"duration": "5", "image_base64": img}
    if res: o["resolution"] = res
    t(f"seedance-2-0-mini 5s res={res}", "seedance-2-0-mini", o)

# caps для hailuo-2-3 opts
print("\n=== hailuo-2-3 opts schema ===")
c = pv.capabilities("hailuo-2-3")
props = c["operations"][0]["requestJsonSchema"]["properties"]["opts"]["properties"]
for k, v in props.items():
    print(k, "->", v.get("enum") or v.get("type"), "|", (v.get("description") or "")[:70])
