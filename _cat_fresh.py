# -*- coding: utf-8 -*-
"""Fresh dump of /api/media-catalog + availability flags."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

cat, _ = pv._req("GET", "/api/media-catalog", auth=False)
open(os.path.join(HERE, "_pv_catalog_fresh.json"), "w", encoding="utf-8").write(
    json.dumps(cat, ensure_ascii=False, indent=1))
ms = cat["models"]
print("keys:", list(cat.keys()))
print("count:", len(ms))
print("model keys union:", sorted({k for m in ms for k in m.keys()}))
kinds = {}
for m in ms:
    kinds[m.get("kind")] = kinds.get(m.get("kind"), 0) + 1
print("by kind:", kinds)
print("\n--- models with a non-empty note / disabled-ish flags ---")
for m in ms:
    flags = {k: v for k, v in m.items()
             if k not in ("params", "variants", "model", "kind", "unit", "note",
                          "inputTypes", "inputModalities")}
    note = m.get("note") or ""
    if note or any(v in (False, "disabled", "off") for k, v in flags.items()):
        print(f"{m.get('kind'):6s} {m['model']:34s} note={note[:60]!r} flags={json.dumps(flags, ensure_ascii=False)[:300]}")
