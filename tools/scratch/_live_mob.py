# -*- coding: utf-8 -*-
"""Живая проверка демо Pages: доехала ли мобильная правка (ждём обновления Pages)."""
import json, time, urllib.request

BASE = 'https://piroman99.github.io/zarynka/vn2/'
NEED = {
    'index.html': ['manifest.webmanifest', 'apple-mobile-web-app-capable', 'id="t-full"', 'id="toast"'],
    'style.css': ['max-aspect-ratio', '100dvh', 'safe-area-inset-top', '#chint', 'max-height:520px'],
    'app.js': ['fitScreens', 'requestFullscreen', 'webkitEnterFullscreen', 'swipedAt'],
    'manifest.webmanifest': ['fullscreen'],
    'sw.js': ["self.addEventListener('fetch'"],
}


def get(name, timeout=20):
    req = urllib.request.Request(BASE + name, headers={'Cache-Control': 'no-cache', 'User-Agent': 'curl/8'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode('utf-8', 'replace')


deadline = time.time() + 300
last = {}
while True:
    ok = True
    for name, marks in NEED.items():
        try:
            st, body = get(name)
        except Exception as e:
            st, body = 'ERR', str(e)
        miss = [m for m in marks if m not in body]
        last[name] = (st, len(body), miss)
        if st != 200 or miss:
            ok = False
    if ok:
        break
    if time.time() > deadline:
        break
    time.sleep(10)

for name, (st, n, miss) in last.items():
    print('%-22s %-5s %7d B  %s' % (name, st, n if isinstance(n, int) else 0,
                                    'ok' if not miss else 'НЕТ: ' + ', '.join(miss)))
print('ИТОГ:', 'живая версия обновлена' if all(not v[2] and v[0] == 200 for v in last.values())
      else 'ещё не доехало/не совпало')
