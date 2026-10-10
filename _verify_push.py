# -*- coding: utf-8 -*-
"""Проверка пуша + числа согласованности персонажа."""
import json, os, subprocess, urllib.request
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "assets", "gen", "kate_overalls_0.png")

print("== remote tree (root, branch=rebuild) ==")
u = "https://api.github.com/repos/piroman99/zarynka/git/trees/rebuild"
try:
    d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "x"}), timeout=30))
    names = [e["path"] for e in d.get("tree", [])]
    print(" entries:", len(names))
    print(" ", ", ".join(names[:20]))
    print(" assets? ", "assets" in names, "| .pv_key leaked? ", ".pv_key" in names)
except Exception as e:
    print(" ERR", e)

print("\n== secrets in remote ==")
for p in (".pv_key", ".api_keys.json"):
    u = f"https://api.github.com/repos/piroman99/zarynka/contents/{p}?ref=rebuild"
    try:
        urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "x"}), timeout=20)
        print(f"  {p}: FOUND (bad!)")
    except urllib.error.HTTPError as e:
        print(f"  {p}: {e.code} (ok)")

print("\n== MAE к эталону (256x256) ==")
a = np.asarray(Image.open(REF).convert("RGB").resize((256, 256)), dtype=np.int16)
for tag in ("nanobanana2", "nanobanana21"):
    vals = []
    for sc in ("s1_reception", "s2_window", "s3_chair"):
        p = os.path.join(HERE, "assets", "gen", f"consist_{tag}__{sc}_0.jpg")
        if os.path.exists(p):
            b = np.asarray(Image.open(p).convert("RGB").resize((256, 256)), dtype=np.int16)
            vals.append(round(float(np.abs(a - b).mean()), 1))
    print(f"  {tag:14s} {vals}  среднее={round(sum(vals)/len(vals),1) if vals else '-'}")
