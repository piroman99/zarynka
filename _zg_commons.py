import json, urllib.request, urllib.parse

def api(params):
    params = dict(params); params['format'] = 'json'
    url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'zaryanka-probe/1.0'})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode())

for q in ['Звёздный городок', 'Star City cosmonaut', 'Zvezdny Gorodok', 'ЦПК Гагарина']:
    for ns in ('6', '14'):
        try:
            d = api({'action': 'query', 'list': 'search', 'srsearch': q,
                     'srnamespace': ns, 'srlimit': 30})
            m = d.get('query', {}).get('search', [])
            print('==', q, 'ns', ns, len(m))
            for x in m:
                print('   ', x['title'])
        except Exception as e:
            print('!!', q, ns, repr(e)[:200])
