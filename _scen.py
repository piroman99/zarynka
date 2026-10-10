# -*- coding: utf-8 -*-
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "scenario.json"), encoding="utf-8"))
print("title:", d.get("title"), "| by:", d.get("by"))
print("cast:", json.dumps(d.get("cast"), ensure_ascii=False)[:300])
for i, s in enumerate(d["scenes"]):
    keys = list(s.keys())
    print(f"\n[{i}] keys={keys}")
    print("   ", json.dumps(s, ensure_ascii=False)[:500])
