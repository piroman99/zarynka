# -*- coding: utf-8 -*-
"""Собирает все кадры сцены «Екатерина Ивановна» из scenario.json."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import frames_vn as F

S = os.path.join(HERE, "assets/sprites")
BG = os.path.join(HERE, "assets/gen/bg_reception_vn_0.png")
KATE, KATE_SAD, SERGEY = (os.path.join(S, n) for n in
                          ("kate_overalls.png", "kate_sad.png", "sergey.png"))
LEFT, RIGHT = 0.30, 0.74

NAMES = {"Сергей": "Сергей Лихнецкий", "Екатерина": "Екатерина Ивановна"}

d = json.load(open(os.path.join(HERE, "scenario.json"), encoding="utf-8"))
scene = next(s for s in d["scenes"] if s["id"] == "kate")

outdir = os.path.join(HERE, "out/scene_kate")
os.makedirs(outdir, exist_ok=True)
made = []
for i, (bg, spk, txt, narr, cam) in enumerate(scene["shots"]):
    kate = KATE_SAD if i >= 10 else KATE
    if narr:
        sprites = [(kate, LEFT, 0.86), (SERGEY, RIGHT, 0.86)]
        name = None
    elif spk == "Екатерина":
        sprites = [(kate, LEFT, 0.90), (SERGEY, RIGHT, 0.80)]
        name = NAMES["Екатерина"]
    else:
        sprites = [(kate, LEFT, 0.80), (SERGEY, RIGHT, 0.90)]
        name = NAMES["Сергей"]
    if narr:
        # ремарки — курсивным тегом в превью не поддержим, просто показываем без имени
        text = txt
    else:
        text = "— " + txt
    out = os.path.join(outdir, f"{i:02d}.png")
    F.frame(BG, out, name=name, text=text, sprites=sprites)
    made.append(out)

print("total frames:", len(made))
