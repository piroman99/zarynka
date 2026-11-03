# -*- coding: utf-8 -*-
"""Дождаться, пока GitHub Pages отдаст сборку с кадрами 9-12 (s5a/s5b) и их озвучкой."""
import hashlib
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://piroman99.github.io/zarynka/vn2/"

local = open(os.path.join(HERE, "vn2", "content.js"), "rb").read()
lm = hashlib.md5(local).hexdigest()
print("локально content.js %d B md5 %s" % (len(local), lm[:10]))
ok = False
for attempt in range(14):
    try:
        with urllib.request.urlopen(BASE + "content.js?cb=%d" % time.time(), timeout=30) as r:
            data = r.read()
        rm = hashlib.md5(data).hexdigest()
        print("попытка %d: %d B md5 %s s5a=%s s5b=%s %s"
              % (attempt + 1, len(data), rm[:10], b'"s5a"' in data, b'"s5b"' in data,
                 "СОВПАЛО" if rm == lm else "ещё старое"), flush=True)
        if rm == lm:
            ok = True
            break
    except Exception as e:
        print("попытка %d: %s" % (attempt + 1, e), flush=True)
    time.sleep(15)

for name in ("img/prolog/s5a.webp", "audio/vo/s5a_00.mp3", "audio/vo/s5a_01.mp3",
             "audio/vo/s5b_00.mp3"):
    try:
        req = urllib.request.Request(BASE + name + "?cb=%d" % time.time(), method="HEAD")
        with urllib.request.urlopen(req, timeout=30) as r:
            print("%-26s %s %s B" % (name, r.status, r.headers.get("Content-Length")))
    except Exception as e:
        print("%-26s FAIL %s" % (name, str(e)[:80]))
for name in ("audio/vo/s5_00.mp3", "audio/vo/s5_01.mp3"):
    try:
        req = urllib.request.Request(BASE + name, method="HEAD")
        with urllib.request.urlopen(req, timeout=30) as r:
            print("%-26s всё ещё отдаётся (старый файл)" % name)
    except Exception as e:
        print("%-26s убран с Pages (ожидаемо)" % name)
print("ИТОГ:", "Pages догнал" if ok else "Pages ещё не отдал сборку")
