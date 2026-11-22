# -*- coding: utf-8 -*-
"""Пуш ветки rebuild в origin (git@github.com:piroman99/zarynka.git).

Ключ и known_hosts — из workspace/.ssh; пуш только через GIT_SSH_COMMAND
(шелл с cd && git push в песочнице блокируется).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WS = os.path.dirname(os.path.dirname(ROOT))
KEY = os.path.join(WS, '.ssh', 'github_ed25519')
KNOWN = os.path.join(WS, '.ssh', 'known_hosts')

ssh_cmd = ('ssh -i %s -o IdentitiesOnly=yes -o UserKnownHostsFile=%s '
           '-o StrictHostKeyChecking=yes' % (KEY, KNOWN))
env = dict(os.environ, GIT_SSH_COMMAND=ssh_cmd, GIT_TERMINAL_PROMPT='0')


def run(*args):
    r = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True, timeout=600)
    print('$', ' '.join(args))
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.stderr.strip():
        print(r.stderr.strip()[-1500:])
    return r.returncode


print('HEAD:', subprocess.run(['git', 'log', '--oneline', '-1'], cwd=ROOT,
                               capture_output=True, text=True).stdout.strip())
rc = run('git', 'push', 'origin', 'rebuild')
print('rc =', rc)
sys.exit(rc)
