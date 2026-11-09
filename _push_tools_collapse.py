# -*- coding: utf-8 -*-
"""Пуш сворачиваемого тулбара: rebuild -> origin, затем зеркало master (слово Ивана
«давай запушим», 2026-11-09). Проверяет, что HEAD ушёл и локальный/удалённый совпали."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    'ssh -i %s/.ssh/github_ed25519 -o IdentitiesOnly=yes '
    '-o UserKnownHostsFile=%s/.ssh/known_hosts -o StrictHostKeyChecking=no' % (WS, WS)))


def run(args):
    r = subprocess.run(args, cwd=HERE, env=ENV, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    print('$ ' + ' '.join(args) + '  -> rc=%d' % r.returncode)
    if out:
        print('  ' + out.replace('\n', '\n  ')[-1200:])
    return r


head = run(['git', 'rev-parse', 'HEAD']).stdout.strip()
print('HEAD:', head)

run(['git', 'push', 'origin', 'rebuild'])
run(['git', 'fetch', 'origin', '--quiet'])
for ref in ('rebuild', 'master'):
    r = run(['git', 'rev-parse', 'origin/' + ref])
    print('  origin/%s = %s' % (ref, r.stdout.strip()))

# зеркало: master = rebuild (--force — ветки не связаны общей историей)
run(['git', 'push', 'origin', 'rebuild:master', '--force'])
run(['git', 'fetch', 'origin', '--quiet'])
run(['git', 'rev-parse', 'origin/master'])
run(['git', 'rev-parse', 'origin/rebuild'])
