# -*- coding: utf-8 -*-
"""Доп. коммит: живая проверка набора букв на опубликованной сборке."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = """vn2: живая проверка набора букв титр-слоя на демо

_live_ovl_type.py — тянет опубликованную сборку с piroman99.github.io и снимает один
и тот же кадр с 0 / N / все буквами (?ovln=N): s3 краски 0 -> 4845 -> 6980 px,
чип s5b 118 -> 675 -> 1479. Геометрия на живом демо (_live_ovl_check.py): 0 проблем."""

FILES = ['_live_ovl_type.py']


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


with open(os.path.join(HERE, '.git_msg.txt'), 'w', encoding='utf-8') as f:
    f.write(MSG)

print('add rc', sh('git add ' + ' '.join('"%s"' % f for f in FILES))[0])
print(sh('git diff --cached --stat')[1])
print('commit rc', sh('git -c user.name="nanobot" -c user.email="nanobot@karpoukhin.ru" '
                     'commit -q -F .git_msg.txt')[0])
print('HEAD', sh('git log --oneline -1')[1])
rc, out, err = sh('git push origin rebuild')
print('push rc', rc, out[-200:], err[-300:])
