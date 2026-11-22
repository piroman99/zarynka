# -*- coding: utf-8 -*-
"""Докинуть в rebuild два проверочных хелпера оглавления (живой Pages + скриншоты)."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    'ssh -i %s/.ssh/github_ed25519 -o IdentitiesOnly=yes '
    '-o UserKnownHostsFile=%s/.ssh/known_hosts -o StrictHostKeyChecking=no' % (WS, WS)))


def run(args):
    r = subprocess.run(args, cwd=HERE, env=ENV, capture_output=True, text=True)
    if r.stdout.strip():
        print(r.stdout.strip()[-1200:])
    if r.returncode:
        print('!!', ' '.join(args), r.returncode, r.stderr[-600:])
    return r


run(['git', 'add', '_live_toc_check.py', '_toc_shots_check.py'])
run(['git', 'commit', '-m', 'vn2: числовые проверки оглавления (живой Pages + скриншоты)'])
p = run(['git', 'push', 'origin', 'rebuild'])
print('push rc', p.returncode)
run(['git', 'log', '--oneline', '-2'])
