# -*- coding: utf-8 -*-
"""Коммит и пуш: метка сцены (tag) — ширина плашки по реальной ширине текста."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = """vn2: пролог — метка сцены больше не обрезается (ширина плашки по тексту)

- _prolog_finals.py: tag() считал ширину чёрной плашки как len(txt)*15 при кегле 30 —
  текст вылезал за плашку во ВСЕХ кадрах (замер _tag_measure.py: «ПЛОЩАДЬ · ЛОЗУНГ»
  312 px текста против 266 px плашки). Теперь x1 = 90 + реальная ширина + 20.
- пересобраны финальные PNG пролога (s1, s3, s4, s5, s5a, s6, s7): метки влезают
- проверка: _tag_sheet.py (лист кропов), _tag_crops.py (нативные кропы x2) — все метки
  с воздухом справа, обрезки нет
- регрессы зелёные: vo_prolog 129.9 с / 0 проблем, cg_range 10/10, ded_credits,
  restart 3/3, auto_menu, ovl_fit 0 проблем"""

FILES = ['_prolog_finals.py', '_tag_measure.py', '_tag_sheet.py', '_tag_check.py',
         '_tag_check2.py', '_tag_check3.py', '_tag_diag.py', '_tag_crops.py',
         '_ovl_shot_s5a.py', '_ovl_dom_s5a.py',
         'assets/final/prolog/s1.png', 'assets/final/prolog/s3.png',
         'assets/final/prolog/s4.png', 'assets/final/prolog/s5.png',
         'assets/final/prolog/s5a.png', 'assets/final/prolog/s6.png',
         'assets/final/prolog/s7.png',
         '_sat/tags_all.png', '_sat/tags_crop.png', '_sat/s5a_final.png']


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


with open(os.path.join(HERE, '.git_msg.txt'), 'w', encoding='utf-8') as f:
    f.write(MSG)

rc, out, err = sh('git add -A ' + ' '.join('"%s"' % f for f in FILES))
print('add rc', rc, err[-300:])
rc, out, err = sh('git -c user.name="nanobot" -c user.email="nanobot@karpoukhin.ru" '
                  'commit -q -F .git_msg.txt')
print('commit rc', rc, out[-200:], err[-400:])
print('HEAD', sh('git log --oneline -1')[1])
print('в индексе осталось:', sh('git status --porcelain | grep -v "^??" | head -5')[1][:200])
rc, out, err = sh('git push origin rebuild')
print('push rc', rc, out[-300:], err[-400:])
