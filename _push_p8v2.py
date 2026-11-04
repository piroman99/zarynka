# -*- coding: utf-8 -*-
"""Коммит и пуш: кадр p8 v2 (гидролаборатория, футуристичный марсианский модуль)."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = """vn2: пролог — кадр p8 v2 «гидролаборатория» (марсианский модуль, глубже бассейн)

- Иван про старый кадр: «там какой-то старый модуль от союза ещё, хочется что-то
  пофутуристичнее марсоподобное и бассейн поглубже»
- _prolog_p8_v2.py (gpt-image-2, 16:9 1K, 5.40 ₽ за A+B): макет под водой заменён на
  новый межпланетный спускаемый модуль (конический экран, гранёный корпус, охристо-
  марсианские и графитовые панели, панорамные окна, радиаторные рёбра, опоры и дюзы,
  стыковочный узел), прямой запрет «Союза»; бассейн-шахта ~20 м вместо 12, дна не видно,
  стенки подсвечены — видны слои глубины
- варианты: A с бортика (видно всю глубину), B камера у воды (низ кадра подводный)
- лист _sat/sheet_p8v2.png + кропы модуля в нативе _sat/sheet_p8v2_detail.png
- в движок НЕ вставлен: ждёт выбора A/B"""

FILES = ['STATUS.md', '_prolog_p8_v2.py', '_p8v2_sheet.py',
         '_pages_wait_p7.py', '_push_p7.py',
         'assets/gen/prolog_p8v2_a__gpt-image-2_0.png',
         'assets/gen/prolog_p8v2_b__gpt-image-2_0.png',
         '_sat/sheet_p8v2.png', '_sat/sheet_p8v2_detail.png',
         '_sat/sheet_p8v2_small.jpg', '_sat/sheet_p8v2_detail_small.jpg',
         '_sat/sheet_p7_vn.png', '_sat/sheet_p7_vn_small.jpg',
         '_sat/p7_p6_last.png', '_sat/p7_p7_p0.png', '_sat/p7_s2_p0.png']


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