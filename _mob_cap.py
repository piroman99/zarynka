# -*- coding: utf-8 -*-
"""Снять экраны vn2 в 3 профилях для листа «до/после»: tag before|after."""
import os, sys, time, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _cdp

TAG = sys.argv[1] if len(sys.argv) > 1 else 'after'
URL = 'file://' + os.path.join(HERE, 'vn2', 'index.html')
OUT = os.path.join(HERE, '.tmp_mob')
os.makedirs(OUT, exist_ok=True)

PROFILES = [('port', 390, 844, 2), ('land', 844, 390, 2), ('desk', 1440, 900, 1)]

b = _cdp.Browser(1600, 900)
made = []
try:
    for name, w, h, dpr in PROFILES:
        b.send('Emulation.setDeviceMetricsOverride', width=w, height=h, deviceScaleFactor=dpr, mobile=(dpr > 1))
        for what, extra, wait in (('title', '', 1.1), ('s1', '&node=2', 1.3)):
            b.navigate(URL + '?instant=1&text=1&voice=0&music=0&preload=0' + extra, wait=wait)
            time.sleep(0.25)
            p = os.path.join(OUT, '%s_%s_%s.png' % (TAG, name, what))
            b.shot(p)
            made.append(os.path.relpath(p, HERE))
            print('ok', os.path.basename(p), os.path.getsize(p), 'B')
        # кинозал (тизер)
        if name == 'port':
            b.navigate(URL + '?instant=1&text=1&voice=0&music=0&preload=0', wait=1.0)
            b.js('document.getElementById("teaser").click()')
            time.sleep(2.2)
            p = os.path.join(OUT, '%s_%s_cinema.png' % (TAG, name))
            b.shot(p)
            made.append(os.path.relpath(p, HERE))
            print('ok', os.path.basename(p), os.path.getsize(p), 'B')
finally:
    b.close()
print(json.dumps(made))
