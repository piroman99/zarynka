import hashlib, os, time, urllib.request

LOCAL = 'vn2/img/prolog/s7.webp'
md5 = hashlib.md5(open(LOCAL, 'rb').read()).hexdigest()
size = os.path.getsize(LOCAL)
print('local s7.webp', size, md5)
URL = 'https://piroman99.github.io/zarynka/vn2/img/prolog/s7.webp'

for i in range(12):
    try:
        req = urllib.request.Request(URL, headers={'User-Agent': 'zaryanka-check/1.0',
                                                   'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=40) as r:
            data = r.read()
        h = hashlib.md5(data).hexdigest()
        print('try %d: %d B  md5 %s  %s' % (i + 1, len(data), h, 'MATCH' if h == md5 else 'old'))
        if h == md5:
            print('Pages отдаёт новый s7.webp')
            break
    except Exception as e:
        print('try %d: !! %s' % (i + 1, repr(e)[:120]))
    time.sleep(20)
