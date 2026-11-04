# -*- coding: utf-8 -*-
"""Почему упал деплой Pages: статусы деплоймента + логи workflow-рана."""
import json
import urllib.request

API = 'https://api.github.com/repos/piroman99/zarynka'
H = {'Accept': 'application/vnd.github+json', 'User-Agent': 'nanobot-zaryanka'}


def get(url, raw=False):
    req = urllib.request.Request(url, headers=H)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    return data if raw else json.loads(data)


deps = get(API + '/deployments?per_page=2')
for d in deps:
    print('deploy %s %s id=%s ref=%s' % (d['sha'][:8], d['created_at'], d['id'], d.get('ref')))
    for s in get('%s/deployments/%s/statuses' % (API, d['id']))[:3]:
        print('   %-11s %s  %s' % (s.get('state'), s.get('created_at'),
                                   (s.get('description') or '')[:200]))
    print('   log_url:', d.get('payload', {}).get('log_url') or '-')

print('\n--- последние workflow-раны ---')
try:
    runs = get(API + '/actions/runs?per_page=3')
    for r in runs.get('workflow_runs', []):
        print('%s %-28s %-9s %s' % (r['head_sha'][:8], r['name'], r['conclusion'],
                                    r['created_at']))
        print('   ', r['html_url'])
except Exception as e:  # noqa: BLE001
    print('runs:', e)

print('\n--- jobs упавшего рана ---')
try:
    runs = get(API + '/actions/runs?per_page=3').get('workflow_runs', [])
    bad = [r for r in runs if r.get('conclusion') == 'failure']
    if not bad:
        print('нет упавших ранов в списке')
    for r in bad[:1]:
        jobs = get(r['jobs_url'] + '?per_page=10').get('jobs', [])
        for j in jobs:
            print('job %-40s %s' % (j['name'], j['conclusion']))
            for st in j.get('steps', []):
                if st.get('conclusion') not in (None, 'success', 'skipped'):
                    print('   шаг %-34s %s' % (st['name'], st['conclusion']))
except Exception as e:  # noqa: BLE001
    print('jobs:', e)
