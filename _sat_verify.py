# -*- coding: utf-8 -*-
"""Проверка, что спрайты не срезаны по верхней кромке кадра + контактный лист кандидатов."""
import os, sys, time, threading, functools, http.server, socketserver
from PIL import Image, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

OUT = os.path.join(HERE, '_sat')
os.makedirs(OUT, exist_ok=True)

class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % PORT

HIDE = """
(function(){var s=document.createElement('style');
 s.textContent='.sprite{visibility:hidden !important}';document.head.appendChild(s);return 1})()
"""

b = Browser(1920, 1080)
try:
    url = BASE + '?instant=1&text=1&voice=0&music=0&auto=0&node=10&page=34'
    b.navigate(url, wait=2.0); time.sleep(0.5)
    with_sp = os.path.join(OUT, '_with.png'); b.shot(with_sp)
    b.js(HIDE); time.sleep(0.5)
    no_sp = os.path.join(OUT, '_without.png'); b.shot(no_sp)
finally:
    b.close(); srv.shutdown()

a = Image.open(with_sp).convert('RGB')
c = Image.open(no_sp).convert('RGB')
diff = ImageChops.difference(a, c).convert('L').point(lambda v: 255 if v > 18 else 0)
print('кадр', a.size, 'маска спрайтов bbox =', diff.getbbox())

# контактный лист
names = ['rec03', 'rec34', 'rec50', 'star01', 's6', 's7']
cw, ch, cols = 960, 540, 2
rows = (len(names) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cw, rows * ch), (12, 14, 20))
for i, nm in enumerate(names):
    p = os.path.join(OUT, 'sat_%s.png' % nm)
    if not os.path.exists(p):
        print('нет', p); continue
    im = Image.open(p).convert('RGB').resize((cw, ch), Image.LANCZOS)
    sheet.paste(im, ((i % cols) * cw, (i // cols) * ch))
sheet.save(os.path.join(OUT, 'sat_sheet.png'))
print('SHEET', sheet.size)
