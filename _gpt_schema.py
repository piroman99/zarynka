# -*- coding: utf-8 -*-
import json
import pv

cap = pv.capabilities('gpt-image-2')
for op in cap.get('operations', []):
    sch = op.get('requestJsonSchema') or {}
    props = (sch.get('properties') or {}).get('opts', {}).get('properties') or {}
    print('OP', op.get('id'))
    for k, v in props.items():
        print('   %-16s %s' % (k, (v.get('type'), v.get('description', ''))[:2]))
