import json, time, urllib.request, urllib.parse

Q = """
[out:json][timeout:60];
(
  way(55.865,38.085,55.890,38.125)["highway"]["name"];
);
out tags 400;
"""

MIRRORS = ['https://overpass.kumi.systems/api/interpreter',
           'https://overpass-api.de/api/interpreter',
           'https://overpass.private.coffee/api/interpreter']

for m in MIRRORS:
    try:
        data = urllib.parse.urlencode({'data': Q}).encode()
        req = urllib.request.Request(m, data=data, headers={'User-Agent': 'zaryanka-probe/1.0'})
        with urllib.request.urlopen(req, timeout=90) as r:
            d = json.loads(r.read().decode())
        els = d.get('elements', [])
        names = sorted({e['tags']['name'] for e in els if e.get('tags', {}).get('name')})
        print('mirror', m, 'streets', len(names))
        for n in names:
            print('  ', n)
        break
    except Exception as e:
        print('!!', m, repr(e)[:120])
        time.sleep(2)
