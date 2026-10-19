# -*- coding: utf-8 -*-
"""Проверка живого демо: content.js и app.js на Pages совпадают с локальными."""
import hashlib, os, time, urllib.request

HERE = "/home/ivan/.nanobot/workspace/novella/zaryanka"
BASE = "https://piroman99.github.io/zarynka/vn2/"
TS = str(int(time.time()))

for name in ("content.js", "app.js", "style.css", "img/bg/cabinet.webp"):
    local = os.path.join(HERE, "vn2", name)
    with open(local, "rb") as f:
        lm = hashlib.md5(f.read()).hexdigest()
    url = BASE + name + "?cb=" + TS
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = r.read()
        rm = hashlib.md5(data).hexdigest()
        print("%-20s %s  локально %s  %s" % (name, "OK " if lm == rm else "РАЗНО",
                                             lm[:8], rm[:8]))
    except Exception as e:
        print(name, "FAIL", e)
