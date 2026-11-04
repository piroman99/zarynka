# -*- coding: utf-8 -*-
"""Поправить цифру расхода в STATUS.md: amend коммита и пуш в rebuild."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.dirname(os.path.dirname(HERE))
KEY = os.path.join(WS, '.ssh', 'github_ed25519')
KNOWN = os.path.join(WS, '.ssh', 'known_hosts')
env = dict(os.environ)
env['GIT_SSH_COMMAND'] = ('ssh -i %s -o IdentitiesOnly=yes -o UserKnownHostsFile=%s '
                          '-o StrictHostKeyChecking=no' % (KEY, KNOWN))

r = subprocess.run(['git', 'add', 'STATUS.md', '_pages_wait_9_12.py', '_commit_9_12.py'],
                   capture_output=True, text=True)
print('add rc', r.returncode, r.stderr[-200:])
r = subprocess.run(['git', 'commit', '--amend', '--no-edit'], capture_output=True, text=True)
print('amend rc', r.returncode, r.stdout[-300:], r.stderr[-200:])
r = subprocess.run(['git', 'push', 'origin', 'HEAD:rebuild', '--force-with-lease'],
                   capture_output=True, text=True, env=env, timeout=300)
print('push rc', r.returncode, r.stdout[-300:], r.stderr[-300:])
r = subprocess.run(['git', 'log', '--oneline', '-2'], capture_output=True, text=True)
print(r.stdout)
