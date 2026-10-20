# -*- coding: utf-8 -*-
"""Снимки страниц, где озвучка раньше расходилась с текстом:
авторская вставка внутри реплики («— Спасибо, — от улыбки…») — теперь своя
страница с голосом закадра. Плюс проверка, какой файл играет элемент voice.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

OUT = os.path.join(HERE, 'assets', 'review')
os.makedirs(OUT, exist_ok=True)
URL = ('file://' + os.path.join(HERE, 'vn2', 'index.html')
       + '?node=10&instant=1&music=0&preload=0&page=%d')

PAGES = [(18, 'a_spasibo'), (19, 'b_vstavka'), (20, 'c_prodolzhenie'),
         (50, 'd_prostite'), (51, 'e_palach'), (52, 'f_ya_ne_mogu')]

b = Browser(1280, 720)
try:
    for pi, tag in PAGES:
        b.navigate(URL % pi, wait=1.0)
        time.sleep(0.5)
        st = b.js(
            "(function(){var v=document.getElementById('voice');"
            "var t=document.getElementById('text')||document.getElementById('tx');"
            "return {src:(v&&v.getAttribute('src'))||'',"
            "text:(t?t.innerText:document.body.innerText).slice(0,120),"
            "name:(document.getElementById('name')||{}).textContent||''};})()")
        print('стр.%d src=%s name=%r' % (pi, os.path.basename(st['src']), st['name']))
        print('   текст: %s' % st['text'].replace('\n', ' ')[:100])
        b.shot(os.path.join(OUT, 'review_113_vo_%s.png' % tag))
finally:
    b.close()
print('готово')
