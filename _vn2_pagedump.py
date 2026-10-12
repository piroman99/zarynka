import json, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
d = json.loads(re.search(r'window\.VN\s*=\s*(\{.*\});?\s*$', src, re.S).group(1))
print('chars =', d.get('chars'))
for i, nd in enumerate(d['nodes']):
    if nd.get('t') == 'scene' and nd.get('id') == 'reception':
        print('node', i, 'reception:', len(nd['pages']), 'pages')
        for p, pg in enumerate(nd['pages']):
            t = (pg.get('who', '') or '') + ('/' + pg['emo'] if pg.get('emo') else '')
            print(f'  {p:2d} [{t:18s}] {pg["tx"][:66]}')
