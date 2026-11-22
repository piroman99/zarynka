# -*- coding: utf-8 -*-
import urllib.request

for u in ("https://piroman99.github.io/zarynka/",
          "https://piroman99.github.io/zarynka/vn2/",
          "https://piroman99.github.io/zarynka/vn2/index.html",
          "https://piroman99.github.io/zaryanka/vn2/"):
    try:
        r = urllib.request.urlopen(u, timeout=20)
        body = r.read()
        print(u, r.status, len(body))
    except Exception as e:
        print(u, "FAIL", e)
