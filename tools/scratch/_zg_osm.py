import json, urllib.request, urllib.parse

Q = """
[out:json][timeout:60];
area["name"="Звёздный городок"]["place"]->.a;
(
  way(area.a)["highway"]["name"];
  node(area.a)["place"];
  way(area.a)["building"]["name"];
  node(area.a)["amenity"];
);
out tags center 200;
"""

def overpass(q):
    data = urllib.parse.urlencode({'data': q}).encode()
    req = urllib.request.Request('https://overpass-api.de/api/interpreter', data=data,
                                 headers={'User-Agent': 'zaryanka-probe/1.0'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())

try:
    d = overpass(Q)
    els = d.get('elements', [])
    print('elements', len(els))
    names = {}
    for e in els:
        t = e.get('tags', {})
        k = (t.get('highway') or t.get('amenity') or t.get('place') or 'bld')
        n = t.get('name') or t.get('name:ru')
        if n:
            names.setdefault(k, set()).add(n)
    for k, v in names.items():
        print('==', k, len(v))
        for n in sorted(v):
            print('   ', n)
except Exception as e:
    print('!!', repr(e)[:300])
