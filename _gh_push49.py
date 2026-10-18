# -*- coding: utf-8 -*-
"""Пуш #49: эмоции Сергея v2 (gpt-image-2) — возраст как у канона."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


MSG = ('vn2: эмоции Сергея v2 (gpt-image-2) — сохранён возраст 42 года: горизонтальные '
       'морщины лба, заломы, гусиные лапки и двухдневная щетина; v1 (омоложенный) в rejected')

print('add:', sh('git add -A')[0])
rc, out, err = sh('git commit -m ' + repr(MSG))
print('commit:', rc, (out or err)[-300:])
rc, out, err = sh('git push origin rebuild')
print('push rebuild:', rc, (out or err)[-200:])
rc, out, err = sh('git push origin rebuild:master --force')
print('mirror master:', rc, (out or err)[-200:])
print('HEAD:', sh('git log --oneline -1')[1][:100])
print('не закоммичено:', (sh("git status --short | grep -v '^??'")[1] or '(чисто)'))
