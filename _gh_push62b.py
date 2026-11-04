# -*- coding: utf-8 -*-
"""Коммит/пуш записи в STATUS.md про фикс кнопки."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))


def sh(cmd, t=600):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


print('add:', sh('git add STATUS.md')[0])
print('commit:', sh('git commit -q -m "docs: note the start-screen button fix"')[0])
print('push rebuild:', sh('git push origin rebuild')[1][-200:])
print('mirror master:', sh('git push origin rebuild:master --force')[1][-200:])
print('HEAD:', sh('git log --oneline -1')[1][:100])
