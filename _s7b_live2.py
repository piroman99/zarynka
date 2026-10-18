import hashlib, os, time, urllib.request

md5 = hashlib.md5(open('vn2/img/prolog/s7.webp', 'rb').read()).hexdigest()
URL = 'https://piroman99.github.io/zarynka/vn2/img/prolog/s7.webp'
for i in range(9):
    req = urllib.request.Request(URL, headers={'User-Agent': 'zaryanka-check/1.0',
                                               'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(req, timeout=40) as r:
        data = r.read()
    h = hashlib.md5(data).hexdigest()
    print('try %d: %d B %s %s' % (i + 1, len(data), h, 'MATCH' if h == md5 else 'old'))
    if h == md5:
        break
    time.sleep(20)
