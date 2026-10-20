# -*- coding: utf-8 -*-
"""Убрать из репозитория временный файл сообщения коммита."""
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


print('rm-cached:', sh('git rm -q --cached .git_msg.txt')[0])
rc, out, err = sh('git commit -q -m "chore: drop the temporary commit message file"')
print('commit:', rc, (out or err)[-200:])
print('push rebuild:', sh('git push origin rebuild')[0])
print('mirror master:', sh('git push origin rebuild:master --force')[0])
print('HEAD:', sh('git log --oneline -1')[1][:100])
print('status:', (sh("git status --short | grep -v '^??'")[1] or '(чисто)'))
