# -*- coding: utf-8 -*-
"""Коммит и пуш: P4 v3 — Сергей со спрайта (только rebuild)."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = """vn2: CG P4 v3 — Сергей как спрайт (щетина, жилет, бейдж)

- Иван забраковал v2: Сергей был выбрит и в галстуке, а на спрайте он небритый,
  в тёмном рабочем жилете поверх бежевой рубашки и с бейджем «ИНЖЕНЕР»
- _cg_p4v3.py: референсы = принятый кабинет cg_room_a + спрайт Сергея + тесный
  кроп лица/жилета/бейджа (_ref_sergey_face_0.png) как жёсткий лок внешности;
  в промпте явные запреты (галстука НЕТ, погон НЕТ) и ровно одна надпись в кадре
- принят вариант A (общий план от окна): CG_P4 = 'cg_p4v3_a', rec_35 пересобран
- регрессы: _vn2_cg_range 10/10, _vn2_ded_credits, _vn2_restart 3/3,
  _vn2_auto_menu, _vn2_start_mobile — всё зелёное"""

FILES = ['STATUS.md', '_vn2_build.py', '_cg_p4v3.py', '_cg_p4v3_sheet.py',
         'vn2/img/cg/rec_35.webp']


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
