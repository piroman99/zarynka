# -*- coding: utf-8 -*-
"""Коммит и пуш: посвящение, титры-ролл, CG стр.48 (ветка rebuild + зеркало master)."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = """vn2: посвящение после значка, титры-ролл, CG стр.48

- посвящение (строки 1 и 3 рассказа) отдельным узлом ded сразу после лого-значка:
  в авто-режиме 7 с, в ручном ждёт клика
- титры в конце серии открываются сами; переделаны в кинематографический ролл
  (снизу вверх, маска по краям, «Пропустить», пропуск по клику/пробелу)
- в титрах Иван Карпухин (piroman99) и nanobot, без придуманных должностей
- CG вариант А на странице 48 приёмной: pg.bg у страницы, спрайты сняты;
  движок сбрасывает инлайновую прозрачность спрайтов при снятии слота
- тесты: новый _vn2_ded_credits.py (21/21); restart/auto/mobile обновлены под
  посвящение и авто-титры"""

FILES = ['CREDITS.md', 'STATUS.md', '_vn2_build.py', '_vn2_restart.py',
         '_vn2_start_mobile.py', '_vn2_ded_credits.py', '_shot_new.py', '_sheet_new.py',
         '_cleanup_diag.py', 'vn2/app.js', 'vn2/content.js', 'vn2/index.html',
         'vn2/style.css', 'vn2/img/cg']


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


rc, out, err = sh('git add ' + ' '.join('"%s"' % f for f in FILES))
print('add rc', rc, out[-200:], err[-300:])
rc, out, err = sh('git -c user.name="nanobot" -c user.email="nanobot@karpoukhin.ru" '
                  'commit -q -F -', t=120)
print('commit rc', rc, out[-300:], err[-300:])
with open(os.path.join(HERE, '.git_msg.txt'), 'w', encoding='utf-8') as f:
    f.write(MSG)
rc, out, err = sh('git -c user.name="nanobot" -c user.email="nanobot@karpoukhin.ru" '
                  'commit -q -F .git_msg.txt')
print('commit rc', rc, out[-300:], err[-400:])
rc, out, err = sh('git log --oneline -1')
print('HEAD', out)
rc, out, err = sh('git push origin rebuild')
print('push rebuild rc', rc, out[-200:], err[-400:])
rc, out, err = sh('git push origin rebuild:master --force')
print('mirror master rc', rc, out[-200:], err[-400:])
