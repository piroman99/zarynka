import json, os, urllib.request, urllib.parse

OUT = 'assets/refs/zg'
os.makedirs(OUT, exist_ok=True)

FILES = [
    'Star City Main Checkpoint.jpg',
    'Star City - The Heroes Alley.jpg',
    'Star City Russia Dom Cosmonavtov.jpg',
    'Zvezdny-gorodok-4860.jpg',
    'Zvezdny-gorodok-4873.jpg',
    'Zvezdny-gorodok-4878.jpg',
    'Zvezdny-gorodok-4895.jpg',
    'Zvezdny-gorodok-h63-4906.jpg',
    'Star City Trade Center.jpg',
    'Star City Russia Church.jpg',
    'Star City Street Sign (5967171097).jpg',
    'Ortstafel Star City.jpg',
    'Star City Surroundings (5968847365).jpg',
    '20140527 star city 9108 (14320431055).jpg',
]

def grab(name, width=1500):
    url = ('https://commons.wikimedia.org/wiki/Special:FilePath/'
           + urllib.parse.quote(name.replace(' ', '_')) + '?width=%d' % width)
    req = urllib.request.Request(url, headers={'User-Agent': 'zaryanka-probe/1.0'})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = r.read()
    ext = '.jpg'
    fn = os.path.join(OUT, name.replace(' ', '_').replace('(', '').replace(')', '').replace(',', ''))
    if not fn.lower().endswith(ext):
        fn += ext
    with open(fn, 'wb') as f:
        f.write(data)
    return fn, len(data)

ok = []
for n in FILES:
    try:
        fn, sz = grab(n)
        print('ok', sz, fn)
        ok.append(fn)
    except Exception as e:
        print('!!', n, repr(e)[:160])

json.dump(ok, open(os.path.join(OUT, '_list.json'), 'w'), ensure_ascii=False, indent=1)
