# -*- coding: utf-8 -*-
"""Полные списки голосов TTS-моделей (enum из capabilities)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

def walk(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == 'voice' and isinstance(v, dict):
                enum = v.get('enum')
                if enum:
                    print('  VOICE enum (%s):' % path, ', '.join(map(str, enum)))
                else:
                    print('  VOICE (%s):' % path, json.dumps(v, ensure_ascii=False)[:300])
            if k == 'voices' and isinstance(v, (list, dict)):
                print('  VOICES (%s):' % path, json.dumps(v, ensure_ascii=False)[:1500])
            walk(v, path + '/' + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + '[%d]' % i)

for m in ('gemini-3.8-flash-tts', 'elevenlabs-v4-tts', 'qwen3-tts'):
    print('===', m)
    try:
        walk(pv.capabilities(m))
    except Exception as e:
        print(' ERR', e)
