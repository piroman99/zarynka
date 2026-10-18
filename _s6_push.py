# -*- coding: utf-8 -*-
"""Коммит + пуш S6 в origin/rebuild (с ключом и known_hosts)."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = ("VN эп1 (vn2): S6 — весенний кадр у ворот Звёздного городка (gpt-image-2, 2.70 ₽/кадр), "
       "выбран вариант B: очередь умеренная, лица нейтральные, пасхалка Женя+Семён; "
       "зима/толпа забракованы Иваном; отклонённые плашки в assets/rejected/s6")

def sh(cmd, t=600):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()

print('commit:', sh('git commit -q -m "%s"' % MSG.replace('"', "'"))[:2])
rc, out, err = sh('git push origin HEAD:rebuild')
print('push:', rc, (out or err)[-300:])
print('HEAD:', sh('git log --oneline -1')[1][:120])
print('remote:', sh('git ls-remote --heads origin rebuild')[1])
print('не закоммичено:', (sh("git status --short | grep -v '^??'")[1] or '(чисто)'))
