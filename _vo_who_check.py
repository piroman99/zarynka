# -*- coding: utf-8 -*-
"""Сверка «кто говорит» (pg.who / pg.vwho по сегментам) с голосом, которым
реально озвучен файл (манифест _voices.json -> voice)."""
import _vo_util as U

man = U.load_manifest()
content = U.load_content()

bad = 0
for nid, k, vo, tx, who in U.segments(content):
    rec = man.get(vo, {})
    got = rec.get('voice')
    if got is None:
        print('?  %s[%d] %s: в манифесте нет голоса' % (nid, k, vo))
        bad += 1
    elif got != who:
        print('!! %s[%d] %s: на странице %s, в файле %s | %s'
              % (nid, k, vo, who, got, tx[:60]))
        bad += 1
print('расхождений: %d' % bad)
