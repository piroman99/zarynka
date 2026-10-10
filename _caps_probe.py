# -*- coding: utf-8 -*-
"""Что принимает MiniMax-Hailuo-02 (и другие видео-модели) — опции и значения."""
import json, pv

for m in ("MiniMax-Hailuo-02", "MiniMax-Hailuo-02-fast", "Kling v3", "kling-v3"):
    try:
        c = pv.capabilities(m)
        print("=====", m, "=====")
        print(json.dumps(c, ensure_ascii=False)[:1500])
        print()
    except Exception as e:
        print("=====", m, "ERR:", str(e)[:200])
        print()

print("=== VIDEO MODELS (list) ===")
try:
    d = pv.models("video")
    print(json.dumps(d, ensure_ascii=False)[:2500])
except Exception as e:
    print("ERR", str(e)[:300])
