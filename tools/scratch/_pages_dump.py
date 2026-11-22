import json, re, sys

s = open('vn2/content.js', encoding='utf-8').read()
s = s[s.index('{'):].rstrip().rstrip(';')
data = json.loads(s)

for n in data['nodes']:
    if n.get('t') != 'scene':
        continue
    print('=== node', n['id'], 'pages', len(n['pages']))
    for i, pg in enumerate(n['pages']):
        cast = pg.get('cast') or {}
        c = ','.join('%s=%s/%s' % (k, v[0], v[1]) for k, v in cast.items() if k != 'speak')
        if cast.get('speak'):
            c += ' speak=%s' % cast['speak']
        bg = ' CG' if pg.get('cg') else ''
        print('%3d%s [%s] %s' % (i, bg, c, pg['tx'][:110].replace('\n', ' ')))
