# -*- coding: utf-8 -*-
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
cat = json.load(open(os.path.join(HERE, "_pv_media-catalog.json"), encoding="utf-8"))
MODELS = ["z-image", "gpt-image-2", "nano-banana-2", "seedream-5-0-flash",
          "grok-imagine", "qwen3-image", "flux-2", "seedream-5-0-pro",
          "nano-banana-2.1", "recraft-v4-1", "flux-2-max", "nano-banana-pro",
          "ideogram-v4", "imagen4", "krea-2", "wan-2-7-image"]
by = {m["model"]: m for m in cat.get("models", [])}
for name in MODELS:
    m = by.get(name)
    if not m:
        print(f"{name}: НЕТ"); continue
    ps = {p.get("key"): p for p in (m.get("params") or [])}
    keys = list(ps)
    def opts(k):
        p = ps.get(k, {})
        return (p.get("options") or [])[:5]
    print(f"\n{name:22s} from={m.get('fromRub')} in={m.get('inputTypes')}")
    print(f"   keys={keys}")
    if "aspect_ratio" in ps: print("     aspect:", opts("aspect_ratio"))
    if "resolution" in ps: print("     res   :", opts("resolution"))
    if "size" in ps: print("     size  :", opts("size"))
    if "quality" in ps: print("     qual  :", opts("quality"))
