# -*- coding: utf-8 -*-
"""Проверка ВСЕХ 51 страниц: движок ставит ровно тот файл, который заявлен в content.js
(chars[who].emos[emo]), и нигде нет отката на нейтраль вместо эмоции."""
import os, glob, json, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
IDX = os.path.join(HERE, 'vn2', 'index.html')

src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))
rec = [n for n in D['nodes'] if n.get('id') == 'reception'][0]
CH = D['chars']

bad = 0
for i, pg in enumerate(rec['pages']):
    url = ('file://' + IDX + '?instant=1&node=9&page=%d&text=1&voice=0&music=0' % i)
    r = subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                        '--disable-gpu', '--virtual-time-budget=4000', '--dump-dom', url],
                       capture_output=True, text=True, timeout=120)
    m = re.search(r'<div id="cast".*?</div>', r.stdout, re.S)
    got = dict(re.findall(r'data-slot="(\d)"[^>]*?src="([^"]*)"', m.group(0) if m else ''))
    exp = {}
    for slot, key in (('0', 'l'), ('1', 'r')):
        c = (pg.get('cast') or {}).get(key)
        if not c:
            continue
        who, emo = c
        ch = CH.get(who) or {}
        url_exp = (ch.get('emos') or {}).get(emo)
        if url_exp is None:
            print('%02d ОТКАТ: %s/%s нет файла эмоции' % (i, who, emo))
            bad += 1
            continue
        exp[slot] = url_exp
    if got != exp:
        print('%02d РАСХОЖДЕНИЕ: ждали %s, в DOM %s' % (i, exp, got))
        bad += 1

print('проверено страниц: %d, проблем: %d' % (len(rec['pages']), bad))
