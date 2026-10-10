# -*- coding: utf-8 -*-
"""Скачать файлы старого репозитория piroman99/zarynka (2016) в assets/orig/zarynka_2016/."""
import os, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "orig", "zarynka_2016")
os.makedirs(OUT, exist_ok=True)
BASE = "https://raw.githubusercontent.com/piroman99/zarynka/master/"
FILES = ["README.md", "LICENSE", "Scenes", "Sprites", "Original text"]

for name in FILES:
    url = BASE + urllib.parse.quote(name)
    dst = os.path.join(OUT, name)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "nanobot-zaryanka/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        with open(dst, "wb") as f:
            f.write(data)
        print(f"OK  {name:16s} {len(data):>7d} B  -> {os.path.relpath(dst, HERE)}")
    except Exception as e:
        print(f"ERR {name:16s} {e}")
