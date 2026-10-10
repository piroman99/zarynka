# -*- coding: utf-8 -*-
"""Музыкальные/аудио модели из каталога PlusVibe."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "_pv_media-catalog.json"), encoding="utf-8"))
for kind in ("music", "audio"):
    ms = [m for m in d["models"] if m.get("kind") == kind]
    print(f"=== {kind} ({len(ms)}) ===")
    for m in sorted(ms, key=lambda x: x.get("fromRub") or 999):
        note = (m.get("note") or "")[:44]
        print(f"  {m['model']:26s} from={m.get('fromRub'):>7} {m.get('unit','')[:14]:14s} {note}")
