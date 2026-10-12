# -*- coding: utf-8 -*-
"""Тест: пауза замораживает печать (снимок длины до/во время паузы/после)."""
import os, re, glob, subprocess, html
HERE = os.path.dirname(os.path.abspath(__file__))
VN2 = os.path.join(HERE, 'vn2')
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*', 'chrome-linux*', 'chrome'))[0]
src = open(os.path.join(VN2, 'index.html'), encoding='utf-8').read()
probe = """<script>
var L=[]; function tl(){var e=document.getElementById('text');return e?e.textContent.length:0;}
setTimeout(function(){L.push('t=1200 pre='+tl());document.getElementById('t-pause').click();},1200);
setTimeout(function(){L.push('t=2100 paused='+tl());},2100);
setTimeout(function(){L.push('t=3000 still='+tl());document.getElementById('t-pause').click();},3000);
setTimeout(function(){L.push('t=4200 resumed='+tl());
  var o=document.createElement('div');o.id='PROBE';o.textContent=L.join(' | ');
  document.body.appendChild(o);},4200);
</script>
"""
test = src.replace('</body>', probe + '</body>')
open(os.path.join(VN2, '_t_p2.html'), 'w', encoding='utf-8').write(test)
IDX = 'file://' + os.path.join(VN2, '_t_p2.html')
p = subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                    '--disable-gpu', '--window-size=1280,720',
                    '--virtual-time-budget=6000', '--dump-dom',
                    IDX + '?node=9&page=0&auto=1&instant=0&text=1&voice=0&music=0'],
                   capture_output=True, text=True, timeout=120)
m = re.search(r'<div id="PROBE">(.*?)</div>', p.stdout, re.S)
print(html.unescape(m.group(1)) if m else '(нет PROBE)')
os.remove(os.path.join(VN2, '_t_p2.html'))
