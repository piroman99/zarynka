# -*- coding: utf-8 -*-
"""Видео и музыка из кэша каталога PlusVibe (цены, единицы)."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "_pv_media-catalog.json"), encoding="utf-8"))
rows = d.get("models", [])
print("videoDisabled:", d.get("videoDisabled"), "| pricesArePlaceholder:", d.get("pricesArePlaceholder"))

for kind in ("video", "music", "audio"):
    ms = [m for m in rows if m.get("kind") == kind]
    print(f"\n=== {kind} ({len(ms)}) ===")
    for m in sorted(ms, key=lambda x: (x.get("fromRub") or 999)):
        note = (m.get("note") or "")[:40]
        print(f"  {m['model']:30s} from={m.get('fromRub'):>7} {m.get('unit',''):16s} {note}")
        for v in (m.get("variants") or [])[:4]:
            if v.get("priceRub") not in (0, None):
                print(f"      · {v.get('addressAs')} = {v.get('priceRub')} ₽ {v.get('label','')}")
