# -*- coding: utf-8 -*-
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
cat = json.load(open(os.path.join(HERE, "_pv_media-catalog.json"), encoding="utf-8"))
models = {m["model"]: m for m in cat.get("models", [])}
for name in ("gpt-4o-mini-tts", "gemini-3.8-flash-tts", "qwen3-tts", "elevenlabs-v4-tts",
             "suno", "lyria-3-5"):
    m = models.get(name)
    print(f"\n===== {name} =====")
    if not m:
        print("  (нет в каталоге)")
        continue
    print("  kind:", m.get("kind"), "| unit:", m.get("unit"), "| fromRub:", m.get("fromRub"))
    print("  inputTypes:", m.get("inputTypes"), "| note:", (m.get("note") or "")[:120])
    for p in (m.get("params") or []):
        print("   -", p.get("key"), "|", p.get("label"), "| type=", p.get("type"),
              "| default=", p.get("default"),
              "| options=", (p.get("options") or [])[:10])
