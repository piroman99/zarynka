# -*- coding: utf-8 -*-
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
cat = json.load(open(os.path.join(HERE, "_pv_media-catalog.json"), encoding="utf-8"))
for m in cat.get("models", []):
    if m.get("kind") != "image":
        continue
    note = (m.get("note") or "").replace("\n", " ")
    print(f"{m['model']:26s} {str(m.get('fromRub')):6s} {note[:110]}")
