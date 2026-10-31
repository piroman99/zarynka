# -*- coding: utf-8 -*-
"""Ждём, пока GitHub Pages отдаст новый p8.webp (сверка размера и хвоста байт)."""
import hashlib
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL = os.path.join(HERE, "vn2", "img", "prolog", "p8.webp")
URL = "https://piroman99.github.io/zarynka/vn2/img/prolog/p8.webp"
want_size = os.path.getsize(LOCAL)
want_md5 = hashlib.md5(open(LOCAL, "rb").read()).hexdigest()
print("локально:", want_size, "B md5", want_md5)

for i in range(1, 41):
    try:
        req = urllib.request.Request(URL + "?cb=%d" % i, headers={"Cache-Control": "no-cache"})
        data = urllib.request.urlopen(req, timeout=25).read()
        got_md5 = hashlib.md5(data).hexdigest()
        ok = len(data) == want_size and got_md5 == want_md5
        print("попытка %2d: %d B md5 %s %s" % (i, len(data), got_md5, "OK" if ok else "старое"))
        if ok:
            print("PAGES ДОГНАЛ")
            break
    except Exception as e:
        print("попытка %2d: ошибка %s" % (i, e))
    time.sleep(5)
