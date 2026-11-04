# -*- coding: utf-8 -*-
"""Отладка живой страницы: что вообще в DOM (стартовый экран, узел, каст)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser  # noqa: E402
from _vn2_nodes import node_index  # noqa: E402

ALLEY = node_index('alley')
url = ('https://piroman99.github.io/zarynka/vn2/index.html'
       '?instant=1&text=1&voice=0&music=0&auto=0&node=%d&page=0' % ALLEY)
b = Browser(1600, 900)
try:
    b.navigate(url, wait=4.0)
    info = b.js("""(() => {
      const st = document.getElementById('stage');
      return {
        title: document.title,
        hasStart: !!document.getElementById('start'),
        startShown: document.getElementById('title') ? document.getElementById('title').className : '',
        stageClass: st ? st.className : '(нет #stage)',
        castHTML: (document.getElementById('cast')||{}).childElementCount,
        castKids: [...document.querySelectorAll('#cast .sprite')].map(s => ({
            src: (s.getAttribute('src')||''), op: getComputedStyle(s).opacity })),
        dbgPos: (window.__DBG && window.__DBG.pos),
        nodes: (window.VN && window.VN.nodes ? window.VN.nodes.length : -1),
        bodyClass: document.body.className
      };})()""")
    print(json.dumps(info, ensure_ascii=False, indent=1))
    print('errors:', b.errors()[:3])
finally:
    b.close()
