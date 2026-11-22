# -*- coding: utf-8 -*-
"""Детальный статус последнего деплоя GitHub Pages (id -> statuses).

    python3 _pages_deploy_status.py
"""
import json
import urllib.request

API = 'https://api.github.com/repos/piroman99/zarynka'


def get(url):
    req = urllib.request.Request(url, headers={
        'Accept': 'application/vnd.github+json', 'User-Agent': 'nanobot-zaryanka'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


try:
    deps = get(API + '/deployments?per_page=3')
except Exception as e:
    raise SystemExit('deployments: %s' % e)

for d in deps[:3]:
    did = d['id']
    print('deploy %s  %s  %s  env=%s' % (d['sha'][:8], d['created_at'], did, d['environment']))
    try:
        sts = get('%s/deployments/%s/statuses' % (API, did))
    except Exception as e:
        print('   statuses: %s' % e)
        continue
    for s in sts[:2]:
        print('   %-12s %s  %s' % (s.get('state'), s.get('created_at'),
                                   (s.get('description') or '')[:100]))
