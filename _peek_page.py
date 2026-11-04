# -*- coding: utf-8 -*-
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
i = src.index('window.VN =')
body = src[i:]
body = body[body.index('{'):].rstrip().rstrip(';')
D = json.loads(body)
p = D['nodes'][10]['pages'][7]
print(json.dumps(p, ensure_ascii=False, indent=1)[:2500])
