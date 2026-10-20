# -*- coding: utf-8 -*-
"""Правда о каждом файле озвучки: какой ТЕКСТ реально в нём звучит.

Проблема: несколько прогонов переиспользования копировали mp3 из чужого файла,
поэтому манифест «что должно быть» расходится с «что записано». Здесь строим
достоверное соответствие по байтам: блоб, у которого в каком-то коммите в
манифесте стоит price>0 (то есть файл РЕАЛЬНО сгенерирован для этого текста),
— эталон. Любой файл, чьи байты равны эталону, содержит тот же текст.

  python3 _vo_truth.py          # отчёт: страницы, где файл звучит не тем текстом
"""
import json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
VO = 'vn2/audio/vo'

def git(*a):
    r = subprocess.run(['git'] + list(a), cwd=HERE, capture_output=True, text=True)
    return r.stdout

def norm(tx):
    t = re.sub(r'^[\u2014\u2013-]+\s*', '', (tx or '').strip())
    t = re.sub(r'[,;:]+$', '', t)
    return re.sub(r'\s+', ' ', t).strip()

def load(txt):
    return json.loads(txt[txt.index('=') + 1:].strip().rstrip(';'))

commits = [c for c in git('log', '--format=%H').split() if c]
man_by_commit = {}
for c in commits:
    raw = git('show', c + ':' + VO + '/_voices.json')
    if raw:
        try:
            man_by_commit[c] = json.loads(raw)
        except Exception:
            pass
print('коммитов с манифестом:', len(man_by_commit))

# эталоны: блоб -> (текст, голос) из записи с price>0
genuine = {}
for c, man in man_by_commit.items():
    for k, v in man.items():
        if not v.get('price'):
            continue
        h = git('rev-parse', '%s:%s/%s' % (c, VO, os.path.basename(k))).strip()
        if not h:
            continue
        key = (norm(v.get('text')), v.get('voice') or 'narr')
        if h in genuine and genuine[h] != key:
            print('  ! блоб с двумя разными текстами: %s -> %r / %r' % (h[:8], genuine[h], key))
        genuine[h] = key
print('эталонных блобов (реально сгенерированных):', len(genuine))

cur = load(open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read())
man = json.load(open(os.path.join(HERE, VO, '_voices.json'), encoding='utf-8'))
rows, bad = [], []
for nd in cur['nodes']:
    for i, pg in enumerate(nd.get('pages') or []):
        vos = pg.get('vo')
        if not vos:
            continue
        vos = [vos] if isinstance(vos, str) else vos
        vtx = pg.get('vtx') or [pg['tx']]
        for j, vo in enumerate(vos):
            p = os.path.join(HERE, 'vn2', vo)
            h = git('hash-object', p).strip() if os.path.exists(p) else ''
            truth = genuine.get(h)
            want = (norm(vtx[j] if j < len(vtx) else pg['tx']),
                    (pg.get('vwho') or [pg.get('who') or 'narr'] * len(vos))[j]
                    if pg.get('vwho') else (pg.get('who') or 'narr'))
            ok = truth == want
            rows.append((nd.get('id'), i, j, vo, want, truth, ok))
            if not ok:
                bad.append(rows[-1])

print('\nфайлов проверено: %d, звучат не тем текстом/голосом: %d' % (len(rows), len(bad)))
for nid, i, j, vo, want, truth, ok in bad:
    print('  %-9s стр.%2d сегм.%d %-18s нужно: %r / %s   звучит: %r / %s'
          % (nid, i, j, os.path.basename(vo), want[0][:46], want[1],
             (truth or ('?', '?'))[0][:46], (truth or ('?', '?'))[1]))
todo_chars = {}
for nid, i, j, vo, want, truth, ok in bad:
    todo_chars[want[1]] = todo_chars.get(want[1], 0) + len(want[0])
print('\nк переозвучке по голосам:')
PRICE = {'narr': 1.70, 'Старик': 1.70, 'Сергей': 1.70, 'Екатерина': 10.84}
tot = 0.0
for k, n in sorted(todo_chars.items(), key=lambda x: -x[1]):
    c = n * PRICE.get(k, 1.70) / 1000
    tot += c
    print('  %-10s %5d зн.  ~%.2f ₽' % (k, n, c))
print('  ИТОГО ~%.2f ₽' % tot)
