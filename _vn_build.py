# -*- coding: utf-8 -*-
"""Строит vn/scenes.js (эпизод 1) из scenario.json + иконки PWA из логотипа."""
import json, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VN = os.path.join(HERE, "vn")
os.makedirs(os.path.join(VN, "icons"), exist_ok=True)

S = json.load(open(os.path.join(HERE, "scenario.json"), encoding="utf-8"))
EP1 = ["title", "commission", "kate", "alley"]

# локация сценария -> картинка (реальный сгенерированный арт, где есть)
BG = {
    "space":  "../assets/gen/ok_x_ship_dock_0.jpg",
    "office": "../assets/gen/ok_reception_fix2_0.jpg",
    "alley":  "../assets/bg_alley.png",
}
SPR = {
    "Сергей":    "../assets/sprites/sergey.png",
    "Екатерина": "../assets/sprites/kate_overalls.png",
    "Лёша":      "",                      # спрайта пока нет — кадр без фигуры
}

out_scenes = []
for sid in EP1:
    s = [x for x in S["scenes"] if x["id"] == sid][0]
    shots = []
    for sh in s["shots"]:
        loc, who, txt = sh[0], sh[1], sh[2]
        cam = sh[4] if len(sh) > 4 else None
        shots.append({
            "bg": BG.get(loc, BG["office"]),
            "who": who or "",
            "name": "",                      # имя для плашки = who (по-русски), ставим ниже
            "text": txt,
            "cam": cam or "",
        })
    out_scenes.append({"id": sid, "title": s["title"], "shots": shots})

data = {"title": S.get("title", "Зарянка"), "episode": "Эпизод 1 · «Приёмная комиссия»",
        "scenes": out_scenes}
with open(os.path.join(VN, "scenes.js"), "w", encoding="utf-8") as f:
    f.write("// Сгенерировано _vn_build.py — не править вручную.\n")
    f.write("window.ZARYANKA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n")
print("scenes.js:", sum(len(s['shots']) for s in out_scenes), "shots")

# --- иконки PWA из логотипа-медальона ---
logo = Image.open(os.path.join(HERE, "assets/gen/logo_b_0.jpg")).convert("RGB")
side = min(logo.size)
logo = logo.crop(((logo.width - side) // 2, (logo.height - side) // 2,
                  (logo.width + side) // 2, (logo.height + side) // 2))
for sz in (192, 512):
    ic = logo.resize((sz, sz), Image.LANCZOS)
    ic.save(os.path.join(VN, "icons", f"icon-{sz}.png"))
print("icons ok")
