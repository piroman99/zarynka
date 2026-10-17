# -*- coding: utf-8 -*-
"""Коммит: лист A/B + журнал по S4, пуш в origin/rebuild."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))
MSG = ('VN эп1 (vn2): S4 — лист A/B «было/стало» на наезде (review_113_s4_cap_ab) + журнал '
       'в STATUS.md и PROLOG_FIXES.md, скрипт _s4_cap_ab.py')


def sh(cmd, t=600):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


for f in ['_s4_cap_ab.py', '_s4_cap_live.py', '_s4_cap_push.py', '_s4_cap_commit.py',
          'assets/review/review_113_s4_cap_ab.png', 'STATUS.md', 'PROLOG_FIXES.md']:
    rc, out, err = sh('git add -- ' + repr(f))
    if rc:
        print('add fail', f, (err or out)[-160:])
print('commit:', sh('git commit -m ' + repr(MSG))[1][-160:])
rc, out, err = sh('git push origin HEAD:rebuild')
print('push:', rc, (out or err)[-200:])
print('HEAD:', sh('git log --oneline -1')[1][:80])
print('remote:', sh('git ls-remote --heads origin rebuild')[1])
print('не закоммичено:', (sh("git status --short | grep -v '^??'")[1] or '(чисто)'))
