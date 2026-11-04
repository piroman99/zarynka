# -*- coding: utf-8 -*-
"""Коммит и пуш: p8 — вариант A (один ряд иллюминаторов) вместо B."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = """vn2: пролог — p8 пересменён на вариант A (один ряд иллюминаторов)

- Иван 2026-11-01: «Не, мне нравится вариант с одним рядом иллюминаторов.
  Как то ламповее и теплее выглядит»
- assets/final/prolog/p8.png = мастер prolog_p8v4_a__gpt-image-2_0.png (_p8_swap_a.py);
  вариант B остаётся мастером в assets/gen, не отклонён и не удалён
- сверка кадра (_p8_check_ab.py): финал совпадает с A по средним (74.2 vs 72.6 у B),
  vn2/img/prolog/p8.webp 492868 B = A после грейда
- без переозвучки и без поднятия VO_VER (текст не менялся)
- пролог: 13 страниц / 130.5 с, проблем 0; регрессы зелёные: cg_range 10/10,
  ded_credits, restart 3/3, auto_menu
- скриншоты и лист пересобраны (_shot_p8.py, _p8_vn_sheet.py)"""

FILES = ['STATUS.md',
         '_p8_swap_a.py', '_p8_bak_drop.py', '_p8_check_ab.py',
         'assets/final/prolog/p8.png',
         'vn2/img/prolog/p8.webp',
         '_sat/p8_p8_p0.png', '_sat/sheet_p8_vn.png', '_sat/sheet_p8_vn_small.jpg']


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


with open(os.path.join(HERE, '.git_msg.txt'), 'w', encoding='utf-8') as f:
    f.write(MSG)

rc, out, err = sh('git add ' + ' '.join('"%s"' % f for f in FILES))
print('add rc', rc, err[-300:])
rc, out, err = sh('git -c user.name="nanobot" -c user.email="nanobot@karpoukhin.ru" '
                  'commit -q -F .git_msg.txt')
print('commit rc', rc, out[-200:], err[-400:])
print('HEAD', sh('git log --oneline -1')[1])
rc, out, err = sh('git push origin rebuild')
print('push rc', rc, out[-300:], err[-400:])
