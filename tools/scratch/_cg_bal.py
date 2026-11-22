# -*- coding: utf-8 -*-
import json
import pv

print(json.dumps(pv.balance(), ensure_ascii=False)[:500])
for m in ('gpt-image-2', 'nano-banana-2.1', 'flux-2'):
    try:
        print(m, json.dumps(pv.capabilities(m), ensure_ascii=False)[:400])
    except Exception as e:
        print(m, 'ERR', str(e)[:200])
