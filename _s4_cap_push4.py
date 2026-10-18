# -*- coding: utf-8 -*-
"""Коммит журнала по S4 (кегль 61) + пуш."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))
MSG = 'VN эп1 (vn2): журнал S4 — кегль 61 (94% ширины экрана ТВ), замеры покой/наезд, лист review_114'


def sh(cmd, t=600):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


for f in ['STATUS.md', 'PROLOG_FIXES.md', '_s4_cap_push3.py', '_s4_cap_push2.py']:
    rc, out, err = sh('git add -- ' + repr(f))
    if rc:
        print('add fail', f, (err or out)[-160:])
print('commit:', sh('git commit -m ' + repr(MSG))[1][-100:])
rc, out, err = sh('git push origin HEAD:rebuild')
print('push:', rc, (out or err)[-140:])
print('HEAD:', sh('git log --oneline -1')[1][:60])
print('remote:', sh('git ls-remote --heads origin rebuild')[1])
print('не закоммичено:', (sh("git status --short | grep -v '^??'")[1] or '(чисто)'))
