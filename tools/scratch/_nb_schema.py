# -*- coding: utf-8 -*-
import json
import pv

cap = pv.capabilities('nano-banana-2.1')
for op in cap.get('operations', []):
    sch = op.get('requestJsonSchema') or {}
    print('OP', op.get('id'))
    print(json.dumps(sch, ensure_ascii=False, indent=1)[:3000])
