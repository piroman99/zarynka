# -*- coding: utf-8 -*-
"""Коммит и пуш: мерцающие звёзды в титрах + замедленный ролл (только rebuild)."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = """vn2: мерцающие звёзды в титрах, ролл медленнее

- .cr-stars: три слоя точек (84/46/20) на radial-gradient, у каждого своя частота
  мерцания (9.5/6.4/4.6 с) и задержка; голубовато-тёплые тона, без картинок и трафика
- генератор блока _credits_stars.py (seed фиксирован, перегенерация на месте
  между маркерами STARS:BEGIN/END), уважает prefers-reduced-motion
- ролл 52 -> 44 px/с: титры читаются тише, «грустнее»
- регресс _vn2_ded_credits.py дополнен проверками звёзд (слои, crTwinkle, частоты)
- готча: instant=1 включает #stage.nofx и глушит все анимации — мерцание мерить
  только без instant"""

FILES = ['STATUS.md', '_vn2_ded_credits.py', '_credits_stars.py', '_shot_stars.py',
         '_check_stars.py', 'vn2/index.html', 'vn2/style.css', 'vn2/app.js']


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


with open(os.path.join(HERE, '.git_msg.txt'), 'w', encoding='utf-8') as f:
    f.write(MSG)

rc, out, err = sh('git add ' + ' '.join('"%s"' % f for f in FILES))
print('add rc', rc, out[-200:], err[-300:])
rc, out, err = sh('git -c user.name="nanobot" -c user.email="nanobot@karpoukhin.ru" '
                  'commit -q -F .git_msg.txt')
print('commit rc', rc, out[-300:], err[-400:])
print('HEAD', sh('git log --oneline -1')[1])
rc, out, err = sh('git push origin rebuild')
print('push rc', rc, out[-300:], err[-400:])
