#!/usr/bin/env python3
"""Живой Pages отдаёт то, что мы только что запушили в rebuild?"""
import os
import time
import urllib.request
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://piroman99.github.io/zarynka/vn2/"

local = {}
for f in ("app.js", "index.html", "style.css"):
    local[f] = open(os.path.join(HERE, "vn2", f), "rb").read()

for attempt in range(12):
    good = 0
    info = []
    for f, data in local.items():
        try:
            req = urllib.request.Request(BASE + f + "?cb=" + str(int(time.time())),
                                         headers={"User-Agent": "nanobot-check"})
            live = urllib.request.urlopen(req, timeout=30).read()
        except Exception as e:
            info.append("%s: %s" % (f, type(e).__name__))
            continue
        same = hashlib.md5(live).hexdigest() == hashlib.md5(data).hexdigest()
        good += 1 if same else 0
        info.append("%s: %s (%d B)" % (f, "совпадает" if same else "старое", len(live)))
    print("попытка %d: %s" % (attempt + 1, "; ".join(info)))
    if good == len(local):
        print("\nЖИВОЕ ДЕМО ОБНОВЛЕНО: все три файла побайтово совпадают с локальными")
        break
    time.sleep(20)
else:
    print("\nPages ещё не обновился (деплой идёт до ~10 мин) — проверить позже")
