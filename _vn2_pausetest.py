# -*- coding: utf-8 -*-
"""Тест кнопки паузы: появляется в авто, переключает ⏸/▶ и замораживает печать."""
import os, re, glob, subprocess, html
HERE = os.path.dirname(os.path.abspath(__file__))
VN2 = os.path.join(HERE, 'vn2')
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*', 'chrome-linux*', 'chrome'))[0]

src = open(os.path.join(VN2, 'index.html'), encoding='utf-8').read()
probe = """<script>
window.__log=[];
function g(id){return document.getElementById(id);}
setTimeout(function(){
  var p=g('t-pause');
  window.__log.push('auto_on='+g('t-auto').classList.contains('on')+' pause_hidden='+p.hidden+' lbl='+p.textContent);
  p.click();
  window.__log.push('after_click: lbl='+p.textContent+' pe='+p.classList.contains('on')+' auto_pause='+g('t-auto').classList.contains('pause'));
  p.click();
  window.__log.push('again: lbl='+p.textContent+' auto_on='+g('t-auto').classList.contains('on'));
  var o=document.createElement('div');o.id='PROBE';o.textContent=window.__log.join(' | ');
  document.body.appendChild(o);
},400);
</script>
"""
test = src.replace('</body>', probe + '</body>')
open(os.path.join(VN2, '_t_pause.html'), 'w', encoding='utf-8').write(test)
IDX = 'file://' + os.path.join(VN2, '_t_pause.html')


def dom(q):
    p = subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                        '--disable-gpu', '--window-size=1280,720',
                        '--virtual-time-budget=3000', '--dump-dom', IDX + '?' + q],
                       capture_output=True, text=True, timeout=120)
    m = re.search(r'<div id="PROBE">(.*?)</div>', p.stdout, re.S)
    return html.unescape(m.group(1)) if m else '(нет PROBE)'


print('АВТО ON :', dom('node=9&page=0&auto=1&instant=1&text=1&voice=0&music=0'))
print('АВТО OFF:', dom('node=9&page=0&instant=1&text=1&voice=0&music=0'))
import os as _os
_os.remove(os.path.join(VN2, '_t_pause.html'))
