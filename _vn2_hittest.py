# -*- coding: utf-8 -*-
"""Реальный hit-test: что за элемент в центре кнопки «Авто» (титул / сцена?)."""
import os, re, glob, subprocess, html
HERE = os.path.dirname(os.path.abspath(__file__))
VN2 = os.path.join(HERE, 'vn2')
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*', 'chrome-linux*', 'chrome'))[0]

src = open(os.path.join(VN2, 'index.html'), encoding='utf-8').read()
probe = """<script>
function probe(){
  var b=document.getElementById('t-auto'), r=b.getBoundingClientRect();
  var el=document.elementFromPoint(r.left+r.width/2, r.top+r.height/2);
  function d(e){return e? (e.id?('#'+e.id):(e.className?('.'+(''+e.className).split(' ')[0]):e.tagName)) : 'null';}
  var out=document.createElement('div'); out.id='PROBE';
  out.textContent='at='+d(el)+' | tools_z='+getComputedStyle(document.getElementById('tools')).zIndex
    +' | title_z='+getComputedStyle(document.getElementById('title')).zIndex
    +' | title_show='+document.getElementById('title').classList.contains('show')
    +' | title_pe='+getComputedStyle(document.getElementById('title')).pointerEvents;
  document.body.appendChild(out);
}
setTimeout(probe, 50);
</script>
"""
test = src.replace('</body>', probe + '</body>')
open(os.path.join(VN2, '_t_hit.html'), 'w', encoding='utf-8').write(test)
IDX = 'file://' + os.path.join(VN2, '_t_hit.html')


def dom(q):
    p = subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                        '--disable-gpu', '--window-size=1280,720',
                        '--virtual-time-budget=2500', '--dump-dom', IDX + '?' + q],
                       capture_output=True, text=True, timeout=120)
    m = re.search(r'<div id="PROBE">(.*?)</div>', p.stdout, re.S)
    return html.unescape(m.group(1)) if m else '(нет PROBE)'


print('ТИТУЛ  :', dom('instant=1'))
print('СЦЕНА  :', dom('node=9&page=0&instant=1'))
