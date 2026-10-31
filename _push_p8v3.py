# -*- coding: utf-8 -*-
"""Коммит и пуш: кадр p8 v3 (межпланетный корабль в сцепке со спускаемым модулем)."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = """vn2: пролог — кадр p8 v3 (межпланетный корабль в сцепке со спускаемым модулем)

- Иван про v2: «тут только посадочный модуль, хотелось бы в сцепке с межпланетным.
  Он сильно больше. Мы в тизере нечто подобное видели»
- _prolog_p8_v3.py (gpt-image-2, 16:9 1K, 8.12 ₽ за A+B) с референсами из тизера:
  ok_space_ship_0.jpg + ok_x_ship_dock_0.jpg
- под водой большой межпланетный корабль (корпус не влезает в кадр, уходит в глубину
  шахты), к носовому узлу через ферму пристыкован маленький спускаемый модуль;
  космонавты и водолаз у стыка задают масштаб; шахта ~20 м, дна не видно
- варианты A (с бортика, по диагонали) и B (камера у воды, низ кадра подводный)
- листы _sat/sheet_p8v3.png + _sat/sheet_p8v3_detail.png (натив: стык, масштаб, буквы)
- в движок НЕ вставлен: ждёт выбора A/B"""

FILES = ['STATUS.md', '_prolog_p8_v3.py', '_p8v3_sheet.py',
         'assets/gen/prolog_p8v3_a__gpt-image-2_0.png',
         'assets/gen/prolog_p8v3_b__gpt-image-2_0.png',
         '_sat/sheet_p8v3.png', '_sat/sheet_p8v3_detail.png',
         '_sat/sheet_p8v3_small.jpg', '_sat/sheet_p8v3_detail_small.jpg']


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
rc, out, err = sh('git push origin rebuild')
print('push rc', rc, out[-300:], err[-400:])