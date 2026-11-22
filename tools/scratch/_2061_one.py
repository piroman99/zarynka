#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request, ssl, os, re, json
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,'.tmp2061')
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA={'User-Agent':'Mozilla/5.0 (X11; Linux) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
def get(u,t=60):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t,context=ctx).read()
# slug -> timestamp
d=json.load(open(os.path.join(OUT,'slugs.json')))
for slug in ['nauchnaia-programma','ekaterina-ivanovna-zarianka','zarianka-2']:
    ts,st=d['iwork'].get(slug,('2016','200')) if slug in d['iwork'] else ('20211018','200')
    u=f'https://web.archive.org/web/{ts}id_/http://2061.su/konkursy/zaryanka-illustrations/iwork/{slug}/'
    try:
        h=get(u).decode('utf-8','replace')
    except Exception as e:
        print(slug,'ERR',e); continue
    open(os.path.join(OUT,f'iwork_{slug}.html'),'w',encoding='utf-8').write(h)
    print('==',slug,len(h))
    for m in re.finditer(r'<img[^>]+src="([^"]+)"', h):
        print('   IMG', m.group(1))
        if len(m.group(1))>10: break
    t=re.findall(r'work__title"><a[^>]*>(.*?)</a>', h, re.S)
    a=re.findall(r'work__author"[^>]*>\s*(.*?)\s*</a>', h, re.S)
    print('   title', t[:2], 'author', a[:2])
