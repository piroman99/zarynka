# -*- coding: utf-8 -*-
"""Пуш правки корневого редиректа: /zarynka/ теперь ведёт на vn2/, а не на старый мок vn/."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))
MSG = "Pages: корневой редирект /zarynka/ ведёт на vn2/ (актуальная сборка), а не на старый мок vn/"


def sh(cmd, t=600):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


print('add:', sh('git add -A -- index.html')[:2])
print('commit:', sh('git commit -q -m "%s"' % MSG)[:2])
rc, out, err = sh('git push origin HEAD:rebuild')
print('push:', rc, (out or err)[-300:])
print('HEAD:', sh('git log --oneline -1')[1][:130])
