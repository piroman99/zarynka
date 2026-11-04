# -*- coding: utf-8 -*-
"""Статус сборки GitHub Pages для piroman99/zarynka (публичный API, без токена).

    python3 _pages_status.py

Печатает: последнюю сборку (status, commit, updated_at, error), а также
подтверждение, что пуш дошёл (git log origin/rebuild).
"""
import json
import os
import subprocess
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    'ssh -i %s/.ssh/github_ed25519 -o IdentitiesOnly=yes '
    '-o UserKnownHostsFile=%s/.ssh/known_hosts -o StrictHostKeyChecking=no' % (WS, WS)))

p = subprocess.run('git fetch -q origin && git log --oneline -1 origin/rebuild',
                   shell=True, cwd=HERE, capture_output=True, text=True, env=ENV)
print('origin/rebuild:', p.stdout.strip() or p.stderr.strip()[:200])
p = subprocess.run('git log --oneline -1', shell=True, cwd=HERE,
                   capture_output=True, text=True, env=ENV)
print('локальный HEAD:', p.stdout.strip())

for url in ('https://api.github.com/repos/piroman99/zarynka/pages/builds/latest',
            'https://api.github.com/repos/piroman99/zarynka/deployments?per_page=3'):
    try:
        req = urllib.request.Request(url, headers={
            'Accept': 'application/vnd.github+json', 'User-Agent': 'nanobot-zaryanka'})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read())
    except Exception as e:
        print(url.split('/')[-1], 'ошибка', str(e)[:120])
        continue
    if isinstance(d, list):
        for it in d:
            print('deploy:', it.get('sha', '')[:8], it.get('environment'),
                  it.get('created_at'), it.get('ref'))
    else:
        print('сборка:', d.get('status'), 'commit', (d.get('commit') or '')[:8],
              d.get('updated_at'), 'error:', (d.get('error') or {}).get('message'))
