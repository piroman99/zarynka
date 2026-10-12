# -*- coding: utf-8 -*-
"""Что умеет TTS: модели и доступные голоса."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

for m in ('gemini-3.8-flash-tts', 'elevenlabs-v4-tts', 'qwen3-tts', 'chatterbox-tts'):
    try:
        c = pv.capabilities(m)
    except Exception as e:
        print(m, 'ERR', e); continue
    print('===', m, '===')
    txt = json.dumps(c, ensure_ascii=False)
    print(txt[:1600])
    print()
