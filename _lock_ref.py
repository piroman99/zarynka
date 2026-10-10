# -*- coding: utf-8 -*-
"""Зафиксировать мастер-референс персонажа + журнал проектных решений.
Локально, без затрат на API. Пишет refs/kate_master.png и refs/lock.json.
"""
import os, json, hashlib, shutil
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REFS = os.path.join(HERE, "refs")
os.makedirs(REFS, exist_ok=True)

SRC = os.path.join(HERE, "assets", "gen", "kate_overalls_0.png")   # утверждённый кадр
MASTER = os.path.join(REFS, "kate_master.png")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


# нормализуем мастер-референс: RGB, ширина 1024
im = Image.open(SRC).convert("RGB")
if im.width != 1024:
    im = im.resize((1024, round(im.height * 1024 / im.width)), Image.LANCZOS)
im.save(MASTER, "PNG")
print("master:", os.path.relpath(MASTER, HERE), im.size, sha(MASTER)[:16])

lock = {
    "character": "Екатерина Ивановна («Зарянка»)",
    "age": 68,                       # ПОДТВЕРДИТЬ: 68 (текст рассказа) vs 50–55 (ТЗ 2016)
    "age_source": "текст рассказа: «пожилая женщина», «бабушка Катя»",
    "engine_consistency": "nano-banana-2.1",
    "engine_look": "flux-2",
    "master_ref": os.path.relpath(MASTER, HERE),
    "master_ref_sha256": sha(MASTER),
    "source_approved": "assets/gen/kate_overalls_0.png",
    "source_approved_sha256": sha(SRC),
    "appearance": (
        "короткие седые вью́щиеся волосы до подбородка, яркие голубые глаза, мягкое доброе "
        "лицо с лёгкими морщинками, спокойная тёплая полуулыбка, стройная, синий рабочий "
        "комбинезон на лямках поверх светлой рубашки"
    ),
    "style": ("аниме-визуальная новелла (гальгэ): чистый лайн-арт, плоская cel-раскраска, "
              "мягкая пастельная палитра, без фотореализма и 3D"),
}
with open(os.path.join(REFS, "lock.json"), "w", encoding="utf-8") as f:
    json.dump(lock, f, ensure_ascii=False, indent=2)
print("lock written:", os.path.relpath(os.path.join(REFS, "lock.json"), HERE))
