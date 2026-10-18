# -*- coding: utf-8 -*-
"""Список голосов gemini-3.8-flash-tts (enum из схемы) + цены TTS."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

c = pv.capabilities('gemini-3.8-flash-tts')
op = c['operations'][0]
props = op['requestJsonSchema']['properties']
print('opts props:', list(props.get('opts', {}).get('properties', {}).keys()))
for k, v in props.get('opts', {}).get('properties', {}).items():
    if 'enum' in v:
        print('\n==', k, '==')
        for x in v['enum']:
            print('   ', x)
    else:
        print('\n==', k, '==', v.get('description', '')[:200])
