# -*- coding: utf-8 -*-
"""Скачать текущую обложку сообщества и сравнить с локальной (MAE)."""
import os, sys, urllib.request
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vk

HERE = os.path.dirname(os.path.abspath(__file__))
local = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "assets", "vk", "cover_b.png")

g = vk.call("groups.getById", group_id=vk.whoami()["id"], fields="cover")
if isinstance(g, dict):
    g = g["groups"][0]
imgs = g["cover"]["images"]
big = max(imgs, key=lambda i: i["width"] * i["height"])
print("live cover:", big["width"], "x", big["height"])
out = os.path.join(HERE, "assets", "vk", "_live_cover.png")
urllib.request.urlretrieve(big["url"], out)

a = np.asarray(Image.open(out).convert("RGB").resize((1920, 768)), dtype=np.float32)
b = np.asarray(Image.open(local).convert("RGB").resize((1920, 768)), dtype=np.float32)
print("MAE live vs local:", round(float(np.abs(a - b).mean()), 3))
