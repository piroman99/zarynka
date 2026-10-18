import hashlib, os, time, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'zaryanka-check/1.0',
                                               'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read()

local_root = open('index.html', 'rb').read()
local_vn = open('vn2/index.html', 'rb').read()
print('local index.html', len(local_root), hashlib.md5(local_root).hexdigest())
print('local vn2/index.html', len(local_vn), hashlib.md5(local_vn).hexdigest())

for url, loc in (('https://piroman99.github.io/zarynka/', local_root),
                 ('https://piroman99.github.io/zarynka/index.html', local_root),
                 ('https://piroman99.github.io/zarynka/vn2/', local_vn),
                 ('https://piroman99.github.io/zarynka/vn2/index.html', local_vn)):
    for i in range(6):
        try:
            data = get(url)
            h = hashlib.md5(data).hexdigest()
            print('%-58s %7d B  %s  %s' % (url, len(data), h,
                                           'MATCH' if h == hashlib.md5(loc).hexdigest() else 'diff'))
            break
        except Exception as e:
            print('%-58s !! %s' % (url, repr(e)[:90]))
            time.sleep(10)
