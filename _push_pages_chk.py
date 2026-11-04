# -*- coding: utf-8 -*-
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


print(sh('git add "_pages_wait_p8a.py"')[0])
print(sh('git -c user.name="nanobot" -c user.email="nanobot@karpoukhin.ru" '
         'commit -q -m "vn2: скрипт проверки Pages для кадра p8 A"')[0:2])
print(sh('git log --oneline -1')[1])
rc, out, err = sh('git push origin rebuild')
print('push', rc, out[-200:], err[-300:])
