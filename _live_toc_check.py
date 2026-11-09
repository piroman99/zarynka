# -*- coding: utf-8 -*-
"""Что реально отдаёт живой GitHub Pages: есть ли в app.js оглавление."""
import os
import ssl
import urllib.request

URL = "https://piroman99.github.io/zarynka/vn2/app.js"
CTX = ssl.create_default_context()
req = urllib.request.Request(URL, headers={"Cache-Control": "no-cache",
                                           "User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
    body = r.read().decode("utf-8", "replace")
print("bytes:", len(body))
for needle in ("zaryanka.progress.v1", "function renderToc", "progDone", "toc-open"):
    print("%-24s %s" % (needle, "ЕСТЬ" if needle in body else "нет"))
