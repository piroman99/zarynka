# -*- coding: utf-8 -*-
"""Скан страниц узла «аллея»: какой page-параметр даёт CG-страницу «Муза».
Печатает (param, фон, проп, спрайты, начало текста) — чтобы увидеть реальное
соответствие параметра и индекса в content.js."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from _cdp import Browser  # noqa: E402
from _vn2_nodes import node_index  # noqa: E402

BASE = 'file://' + os.path.join(ROOT, 'vn2', 'index.html')
GEO = """
(function(){
  var b=document.querySelector('.bg.on');
  var sp=[].filter.call(document.querySelectorAll('.sprite'),
        function(e){return getComputedStyle(e).opacity!=='0';}).length;
  var p=document.querySelector('#props .prop');
  return {bg:b?b.style.backgroundImage:'', prop:!!(p&&p.classList.contains('on')),
          sprites:sp, tx:(document.getElementById('text').textContent||'').trim().slice(0,34)};
})()
"""
AL = node_index('alley')
b = Browser(1280, 720)
try:
    for param in range(16, 22):
        b.navigate(BASE + '?node=%d&page=%d&instant=1&text=1&voice=0&music=0' % (AL, param), wait=2.0)
        b.wait_js("(document.querySelector('.bg.on')||{}).style.backgroundImage !== ''", timeout=20)
        g = b.js(GEO)
        print('page=%-2d %-30s проп=%-5s спр=%d  %r'
              % (param, g['bg'][:30], g['prop'], g['sprites'], g['tx']))
finally:
    b.close()
