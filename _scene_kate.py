# -*- coding: utf-8 -*-
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "scenario.json"), encoding="utf-8"))
for s in d["scenes"]:
    if s["id"] == "kate":
        print("SCENE:", s["id"], "/", s["title"], "shots:", len(s["shots"]))
        for i, sh in enumerate(s["shots"]):
            bg, spk, txt, narr, cam = sh
            print(f"[{i:02d}] bg={bg} spk={spk} narr={narr} cam={cam}\n     {txt}")
