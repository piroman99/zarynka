#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request, ssl, re, json, os
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,'.tmp2061')
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA={'User-Agent':'Mozilla/5.0'}
def cdx(pattern):
    u=f'http://web.archive.org/cdx/search/cdx?url={pattern}&output=text&fl=original,timestamp,statuscode&collapse=urlkey&limit=2000'
    req=urllib.request.Request(u,headers=UA)
    return urllib.request.urlopen(req,timeout=90,context=ctx).read().decode('utf-8','replace')

txt=cdx('2061.su/konkursy/zaryanka-illustrations/*')
rows=[l.split() for l in txt.strip().splitlines() if l.strip()]
print('CDX rows:', len(rows))
iw={}; wk={}
for r in rows:
    if len(r)<3: continue
    url,ts,st=r[0],r[1],r[2]
    m=re.search(r'/iwork/([^/]+)/?$', url)
    if m: iw.setdefault(m.group(1),(ts,st)); continue
    m=re.search(r'/work/([^/]+)/?$', url)
    if m: wk.setdefault(m.group(1),(ts,st))
print('iwork slugs:', len(iw))
print('work slugs:', len(wk))
json.dump({'iwork':iw,'work':wk}, open(os.path.join(OUT,'slugs.json'),'w'), ensure_ascii=False, indent=1)
print(sorted(iw.keys())[:80])
