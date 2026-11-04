# -*- coding: utf-8 -*-
"""Коммит и пуш в rebuild: фикс титр-слоя (em -> проценты кадра) + проверка."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = """vn2: титр-слой кадров — надписи больше не уезжают в левый верхний угол

Причина одной правкой на все кадры пролога: в applyOvl() позиция строки задавалась
в em (x/2400 em), а em в left/top считается от СВОЕГО font-size элемента (кегль
строки), а не от ширины кадра. Строка уходила в левый верхний угол и обрезалась краем;
плашки (<i>, без своего font-size) стояли правильно — отсюда «пустые» прямоугольники.

- vn2/app.js: позиции строк и размеры плашек в ПРОЦЕНТАХ кадра (x/2400, y/1350);
  кегль по-прежнему em относительно #ovl (font-size = ширина кадра). Координаты
  в _vn2_build.py не менялись, масштабирование на любой экран сохранено.
- _ovl_inside.py: пиксельная проверка «строка внутри плашки и по центру» — 0 проблем,
  отличие центра <= 2 px на всех страницах с ovl (s3, s4, s5a x2, s5b).
- _ovl_dom_all.py: DOM-дамп геометрии всех страниц с ovl.
- STATUS.md: разбор бага + открытый нюанс с камерой на s4.
- Регрессы: _ovl_fit 0, vo пролога 129.9 с / 0, cg_range 10/10, ded_credits,
  restart 3/3, auto_menu."""

FILES = ['vn2/app.js', 'STATUS.md', '_ovl_inside.py', '_ovl_dom_all.py']


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


with open(os.path.join(HERE, '.git_msg.txt'), 'w', encoding='utf-8') as f:
    f.write(MSG)

rc, out, err = sh('git add ' + ' '.join('"%s"' % f for f in FILES))
print('add rc', rc, err[-200:])
rc, out, err = sh('git diff --cached --stat')
print(out)
rc, out, err = sh('git -c user.name="nanobot" -c user.email="nanobot@karpoukhin.ru" '
                  'commit -q -F .git_msg.txt')
print('commit rc', rc, err[-300:])
print('HEAD', sh('git log --oneline -1')[1])
rc, out, err = sh('git push origin rebuild')
print('push rc', rc, out[-300:], err[-400:])