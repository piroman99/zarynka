# -*- coding: utf-8 -*-
"""Пуш #55: значок перехода — пятиугольник-жетон."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


print('add:', sh('git add -A')[0])
rc, out, err = sh('git commit -q -F .git_msg.txt')
print('commit:', rc, (out or err)[-400:])
if rc == 0:
    os.remove(os.path.join(HERE, '.git_msg.txt'))
print('push rebuild:', sh('git push origin rebuild')[0])
print('mirror master:', sh('git push origin rebuild:master --force')[0])
print('HEAD:', sh('git log --oneline -1')[1][:110])
print('status:', (sh("git status --short | grep -v '^??'")[1] or '(чисто)'))
