# -*- coding: utf-8 -*-
"""Коммит и пуш: webp кадров пролога пересобраны после правки метки (tag)."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = """vn2: пролог — webp кадров пересобраны с исправленной меткой сцены

- _vn2_build.py перегнал assets/final/prolog -> vn2/img/prolog после правки tag()
  (первый прогон шёл ДО правки, поэтому в webp метка ещё была обрезанной)
- затронуты s1, s3, s4, s5, s5a, s6, s7; content.js и озвучка не менялись"""

FILES = ['vn2/img/prolog/s1.webp', 'vn2/img/prolog/s3.webp', 'vn2/img/prolog/s4.webp',
         'vn2/img/prolog/s5.webp', 'vn2/img/prolog/s5a.webp', 'vn2/img/prolog/s6.webp',
         'vn2/img/prolog/s7.webp']


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


with open(os.path.join(HERE, '.git_msg.txt'), 'w', encoding='utf-8') as f:
    f.write(MSG)

rc, out, err = sh('git add -A ' + ' '.join('"%s"' % f for f in FILES))
print('add rc', rc, err[-200:])
rc, out, err = sh('git -c user.name="nanobot" -c user.email="nanobot@karpoukhin.ru" '
                  'commit -q -F .git_msg.txt')
print('commit rc', rc, err[-300:])
print('HEAD', sh('git log --oneline -1')[1])
rc, out, err = sh('git push origin rebuild')
print('push rc', rc, out[-200:], err[-300:])
