# -*- coding: utf-8 -*-
"""Список доступных голосов TTS (enum из схемы)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv


def find_enums(obj, path=''):
    out = []
    if isinstance(obj, dict):
        if 'enum' in obj and isinstance(obj['enum'], list):
            out.append((path, obj['enum']))
        for k, v in obj.items():
            out += find_enums(v, path + '.' + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += find_enums(v, path + '[%d]' % i)
    return out


for m in ('gemini-3.8-flash-tts', 'elevenlabs-v4-tts', 'qwen3-tts', 'chatterbox-tts'):
    try:
        c = pv.capabilities(m)
    except Exception as e:
        print(m, 'ERR', e); continue
    print('===', m)
    for path, e in find_enums(c):
        if 'voice' in path.lower() or 'speaker' in path.lower() or 'voice' in ' '.join(map(str, e)).lower():
            print('  ', path, '=', e)
