# -*- coding: utf-8 -*-
"""Коммит: аккуратная вырезка спрайта поэта (петли волос, серая кайма).

Запуск: python3 _push_poet_hair.py
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    'ssh -i %s/.ssh/github_ed25519 -o IdentitiesOnly=yes '
    '-o UserKnownHostsFile=%s/.ssh/known_hosts -o StrictHostKeyChecking=no' % (WS, WS)))

MSG = """vn2: спрайт поэта — аккуратная вырезка волос (петли и серая кайма)

- Иван 2026-11-04: «волосы в спрайте поэта неровно вырезались, особенно где петли»
- причина: cutout() сборки — flood-fill от края (tol=34) + blur альфы 1.1; фон, замкнутый
  петлёй волос, оставался непрозрачным серым пятном, по контуру — серая кайма
- _poet_matte.py: мягкая альфа по цвету фона (рампа 12->40), ЛЮБАЯ замкнутая область фона
  <=60000 px считается фоном (петли волос), despill снимает вклад фона у полупрозрачных
- _poet_norm.py матирует и нормирует по альфе; CHAR_SRC отдаёт RGBA, сборка такие файлы
  не режет (флаг pre-matted) и пишет webp без потерь
- замер _poet_hair_check.py: серых пятен внутри фигуры 41 926 px -> 0; в игровом poet.webp
  7072 пятна + 7914 px каймы -> 0 пятен, 169 px каймы; петли прозрачные (22)
- нормировка цела: плечи/холст 0.560 у всех шести эмоций; cg_range 10/10, эмоции 57/57,
  ded_credits и start_mobile зелёные
"""

def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()

open(os.path.join(HERE, '.git_msg_poet_hair.txt'), 'w', encoding='utf-8').write(MSG)
print('add:', sh('git add -A')[0])
print('commit:', sh('git commit -q -F .git_msg_poet_hair.txt')[0])
print('HEAD:', sh('git log --oneline -1')[1][:110])
rc, out, err = sh('git push origin rebuild')
print('push rebuild rc=%d %s %s' % (rc, out[-160:], err[-200:]))
rc, out, err = sh('git push origin rebuild:master --force')
print('mirror master rc=%d %s %s' % (rc, out[-160:], err[-200:]))
