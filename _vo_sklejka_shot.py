# -*- coding: utf-8 -*-
"""Снимки склеенных страниц — индекс страницы ищем по фрагменту текста."""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

OUT = os.path.join(HERE, 'assets', 'review')
URL = ('file://' + os.path.join(HERE, 'vn2', 'index.html')
       + '?node=10&instant=1&music=0&preload=0&page=%d')

src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('{'):src.rindex('}') + 1])
rec = [n for n in D['nodes'] if n.get('id') == 'reception'][0]


def find(frag):
    for i, pg in enumerate(rec['pages']):
        if frag in pg['tx']:
            return i
    raise SystemExit('не найдено: ' + frag)


CASES = [('Действительно интересно', 'a_do_spasibo'),
         ('от улыбки вокруг её глаз', 'b_sklejka_spasibo'),
         ('мне помогали несколько моих', 'c_prodolzhenie'),
         ('Даже если вы останетесь', 'd_do_prostite'),
         ('Сергей чувствовал себя палачом', 'e_sklejka_prostite'),
         ('я не могу принять у вас', 'f_prodolzhenie2'),
         ('она внезапно тепло улыбнулась', 'g_sklejka_final')]

b = Browser(1280, 720)
try:
    for frag, tag in CASES:
        pi = find(frag)
        b.navigate(URL % pi, wait=1.0)
        time.sleep(0.5)
        st = b.js(
            "(function(){var v=document.getElementById('voice');"
            "var t=document.getElementById('text');"
            "return {src:(v&&v.getAttribute('src'))||'',"
            "text:(t?t.innerText:'').slice(0,120),"
            "name:(document.getElementById('name')||{}).textContent||''};})()")
        print('стр.%d src=%s name=%r' % (pi, os.path.basename(st['src']), st['name']))
        print('   текст: %s' % st['text'].replace('\n', ' ')[:110])
        b.shot(os.path.join(OUT, 'review_114_sklejka_%s.png' % tag))
finally:
    b.close()
print('готово')
