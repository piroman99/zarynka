# -*- coding: utf-8 -*-
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv
for m in ("gemini-3.8-flash-tts",):
    cap = pv.capabilities(m)
    print(m, '=> limits:', json.dumps(cap.get('limits'), ensure_ascii=False))
    print('   ops:', json.dumps(cap.get('operations'), ensure_ascii=False)[:300])
