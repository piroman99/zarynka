# -*- coding: utf-8 -*-
"""Коммит и пуш: чип кадра 12 (s5b) выровнен по центру кадра (вариант A)."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = """vn2: пролог — чип кадра 12 (s5b) по центру кадра

- OVL_PAGES[('s5b',0)]: плашка 801..1599 (центр 1200 вместо 960), y 690..780,
  текст y 735 — вариант A, выбран Иваном
- причина: центр чипа стоял на x=960 при центре кадра 1200 -> висел левее на 240 px
- пересобран content.js; кадры, озвучка и остальные страницы не менялись"""

FILES = ['_vn2_build.py', 'vn2/content.js']

def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()

with open(os.path.join(HERE, '.git_msg.txt'), 'w', encoding='utf-8') as f:
    f.write(MSG)

rc, out, err = sh('git add ' + ' '.join('"%s"' % f for f in FILES))
print('add rc', rc, err[-200:])
rc, out, err = sh('git -c user.name="nanobot" -c user.email="nanobot@karpoukhin.ru" '
                  'commit -q -F .git_msg.txt')
print('commit rc', rc, err[-300:])
print('HEAD', sh('git log --oneline -1')[1])
rc, out, err = sh('git status --short')
print('status', out[:300])
rc, out, err = sh('git push origin rebuild')
print('push rc', rc, out[-300:], err[-300:])
