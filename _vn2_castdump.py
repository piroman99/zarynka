import json, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
d = json.loads(re.search(r'window\.VN\s*=\s*(\{.*\});?\s*$', src, re.S).group(1))
print('chars manifest:')
for who, v in d.get('chars', {}).items():
    print('  ', who, '-> base', v['base'], '| emos', list(v['emos'].keys()))
for i, nd in enumerate(d['nodes']):
    if nd.get('t') == 'scene' and nd.get('id') == 'reception':
        print('reception pages:', len(nd['pages']))
        for p, pg in enumerate(nd['pages']):
            c = pg.get('cast', {})
            l = c.get('l'); r = c.get('r')
            ls = ('%s/%s' % (l[0][:3], l[1])) if l else '---'
            rs = ('%s/%s' % (r[0][:3], r[1])) if r else '---'
            tag = pg.get('who', '')
            print(f'  {p:2d} L:{ls:14s} R:{rs:14s} speak:{c.get("speak",""):9s} who:{tag:9s} {pg["tx"][:52]}')
