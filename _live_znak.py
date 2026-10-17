# -*- coding: utf-8 -*-
"""Живая проверка демо: Pages отдаёт новый значок и content.js с новым путём."""
import json, time, urllib.request, urllib.error

BASE = 'https://piroman99.github.io/zarynka/'
VID = BASE + 'out/znak3d_rot.mp4'
CJS = BASE + 'vn2/content.js'


def get(url, method='GET', tries=30, pause=10):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, method=method,
                                         headers={'Cache-Control': 'no-cache'})
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.status, r.read() if method == 'GET' else b'', dict(r.headers)
        except urllib.error.HTTPError as e:
            last = 'HTTP %s' % e.code
        except Exception as e:
            last = str(e)
        time.sleep(pause)
    return None, last, {}


st, body, hdr = get(VID, 'HEAD')
print('значок:', st, '| size', hdr.get('Content-Length'), '| type', hdr.get('Content-Type'))

st2, cjs, _ = get(CJS)
print('content.js:', st2, '| длина', len(cjs) if isinstance(cjs, bytes) else cjs)
if isinstance(cjs, bytes):
    t = cjs.decode('utf-8', 'replace')
    print('  путь значка в content.js:',
          [l.strip() for l in t.splitlines() if 'znak3d' in l])

st3, body3, hdr3 = get(VID, 'GET')
if isinstance(body3, bytes) and body3:
    print('скачано байт:', len(body3), '| совпадает с локальным:',
          len(body3) == 427131)
