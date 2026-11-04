# -*- coding: utf-8 -*-
"""Коммит и пуш кадра s1 (стена/подворотня) + p6 (лунная станция) в `rebuild`.

Иван 2026-11-04: «S1 — новый кадр „Звёздный городок, стена, полустёртое граффити“;
P6 — композит не надо, это лунная станция, пересобери». Выбраны варианты B и B.

Запуск: python3 _push_s1_p6.py [--dry]
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    'ssh -i %s/.ssh/github_ed25519 -o IdentitiesOnly=yes '
    '-o UserKnownHostsFile=%s/.ssh/known_hosts -o StrictHostKeyChecking=no' % (WS, WS)))

MSG = """vn2: пролог — кадр s1 стена Звёздного городка, кадр p6 лунная станция

- Иван 2026-11-04: первый кадр пролога — стена с полустёртым граффити «МАРС — ДЕЛО
  ОБЩЕЕ»; p6 пересобран как ЛУННАЯ станция: композит не нужен, марсианской охры нет
- новый кадр s1a (gpt-image-2, _prolog_s1_wall.py; выбран вариант B — угол двора);
  узел s1 теперь ДВЕ страницы: стена (стр. 1) -> подворотня (стр. 2), кроссфейд .bg
- PAGE_BG в _vn2_build.py: кадр отдельной страницы внутри узла (pg.bg = img/prolog/s1a)
- подпись «МАРС — ДЕЛО ОБЩЕЕ?» снята с кадра подворотни: надпись живёт в граффити
- p6 = p6luna_b (_prolog_p6_luna.py, референс — арт станции из тизера), марсианский
  мастер и композиты p6_base_var* убраны в assets/rejected/p6/
- озвучка s1_00/s1_01 переписана (Charon, 0.59 RUB), VO_VER 5 -> 6, манифест синхронен
- пролог 130.3 с / 0 проблем; регрессы ded_credits, cg_range 10/10, auto_menu,
  start_mobile, restart зелёные
"""


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


if '--dry' in sys.argv:
    print(sh('git status --porcelain')[:2], '\n', MSG)

print('add:', sh('git add -A')[0])
rc, out, err = sh('git commit -q -F .git_msg_s1p6.txt' if os.path.exists(os.path.join(HERE, '.git_msg_s1p6.txt'))
                  else 'git commit -q -m %s' % repr(MSG))
if rc:
    print('commit rc=%d %s %s' % (rc, out[:300], err[:300]))
print('HEAD:', sh('git log --oneline -1')[1][:120])
rc, out, err = sh('git push origin rebuild')
print('push rebuild rc=%d %s %s' % (rc, out[-200:], err[-300:]))
rc, out, err = sh('git push origin rebuild:master --force')
print('mirror master rc=%d %s %s' % (rc, out[-200:], err[-300:]))
