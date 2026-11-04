# -*- coding: utf-8 -*-
"""Коммит и пуш: CG-диапазоны (P4 v2 на 35..37, грустный CG до 61) + выход Екатерины.

Пушим ТОЛЬКО rebuild — зеркало master (демо на Pages) обновим после того,
как Иван выберет вариант A/B кадра P4.
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = """vn2: CG диапазоном + выход Екатерины на приветствии

- CG теперь может держаться НЕСКОЛЬКО страниц (CG_RANGES в _vn2_build.py):
  от якоря начала до якоря конца включительно, спрайты внутри сняты
- P4 v2 (rec_35) на стр. 22-23: «Сергей потер переносицу» → «При всех наших
  технических возможностях». Новый кабинет по референсу принятого CG приёмной,
  форма Сергея со спрайта, за окном весна и корпуса Звёздного городка
- грустный CG (rec_48) продлён со стр. 48 до 50 включительно
- выход Екатерины перенесён на «Добрый день. Добро пожаловать в Звездный
  городок»: описание внешности идёт без спрайта, вход = приветствие Сергея
- регресс _vn2_cg_range.py (10/10); в тестах обязателен auto=0, иначе короткие
  страницы сами уезжают за время ожидания и замер врёт"""

FILES = ['STATUS.md', '_vn2_build.py', '_vn2_cg_range.py', '_cg_p4v2.py', '_cg_rec23.py',
         '_shot_cg35.py', '_sheet_p4v2.py', '_pages_dump.py',
         'vn2/content.js', 'vn2/img/cg']


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


with open(os.path.join(HERE, '.git_msg.txt'), 'w', encoding='utf-8') as f:
    f.write(MSG)

rc, out, err = sh('git add ' + ' '.join('"%s"' % f for f in FILES))
print('add rc', rc, out[-300:], err[-300:])
rc, out, err = sh('git -c user.name="nanobot" -c user.email="nanobot@karpoukhin.ru" '
                  'commit -q -F .git_msg.txt')
print('commit rc', rc, out[-300:], err[-400:])
rc, out, err = sh('git log --oneline -1')
print('HEAD', out)
rc, out, err = sh('git push origin rebuild')
print('push rebuild rc', rc, out[-300:], err[-400:])
