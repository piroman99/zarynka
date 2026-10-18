# -*- coding: utf-8 -*-
"""Дождаться, пока Pages отдаст новую сборку: Старик в chars + новый размер rec_48."""
import json, os, time, urllib.request

BASE = 'https://piroman99.github.io/zarynka/vn2/'
HERE = os.path.dirname(os.path.abspath(__file__))


def get(url, head=False):
    req = urllib.request.Request(url, method='HEAD' if head else 'GET',
                                 headers={'User-Agent': 'Mozilla/5.0',
                                          'Cache-Control': 'no-cache'})
    r = urllib.request.urlopen(req, timeout=30)
    return r.read() if not head else int(r.headers.get('Content-Length') or 0)


for attempt in range(30):
    try:
        txt = get(BASE + 'content.js?x=%d' % attempt).decode('utf-8')
        D = json.loads(txt[txt.index('=') + 1:].strip().rstrip(';'))
        chars = list(D['chars'])
        loc = os.path.getsize(os.path.join(HERE, 'vn2', 'audio', 'vo', 'rec_48.mp3'))
        rem = get(BASE + 'audio/vo/rec_48.mp3', head=True)
        print('попытка %d: chars=%s rec_48 demo=%s local=%s' % (attempt + 1, chars, rem, loc))
        if 'Старик' in chars and rem == loc:
            print('PAGES ОБНОВИЛСЯ')
            break
    except Exception as e:
        print('попытка %d: %s' % (attempt + 1, e))
    time.sleep(20)
