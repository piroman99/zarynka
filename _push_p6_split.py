# -*- coding: utf-8 -*-
"""Коммит: кадр p6 делится пополам (Марс на стр. 1, лунная станция на стр. 2).

Запуск: python3 _push_p6_split.py
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    'ssh -i %s/.ssh/github_ed25519 -o IdentitiesOnly=yes '
    '-o UserKnownHostsFile=%s/.ssh/known_hosts -o StrictHostKeyChecking=no' % (WS, WS)))

MSG = """vn2: пролог — кадр p6 делится пополам: Марс (стр. 1) + лунная база (стр. 2)

- Иван 2026-11-04: «мы его делим попалам: p6 — страница 1 старую с Марсом верни,
  p6-2 как раз с лунной станцией»
- p6.png = старый марсианский мастер, возвращён из assets/rejected/p6/
- p6luna.png = p6luna_b (лунная станция, _prolog_p6_luna.py) на стр. 2
- PAGE_BG[('p6', 1)] = img/prolog/p6luna — смена кадра внутри узла (.bg кроссфейд)
- композит _p6_base.py остаётся снятым, марсианской охры в лунном кадре нет
- регрессы ded_credits, cg_range 10/10, auto_menu, start_mobile, restart — зелёные,
  пролог 130.3 с / 0 проблем, js-ошибок 0
"""


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


open(os.path.join(HERE, '.git_msg_p6split.txt'), 'w', encoding='utf-8').write(MSG)
print('add:', sh('git add -A')[0])
print('commit:', sh('git commit -q -F .git_msg_p6split.txt')[0])
print('HEAD:', sh('git log --oneline -1')[1][:110])
rc, out, err = sh('git push origin rebuild')
print('push rebuild rc=%d %s %s' % (rc, out[-160:], err[-200:]))
rc, out, err = sh('git push origin rebuild:master --force')
print('mirror master rc=%d %s %s' % (rc, out[-160:], err[-200:]))
