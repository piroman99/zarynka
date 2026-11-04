# -*- coding: utf-8 -*-
"""Коммит: Екатерина входит на описании («кудрявые седые, как снег, волосы»).

Запуск: python3 _push_kate_enter.py
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    'ssh -i %s/.ssh/github_ed25519 -o IdentitiesOnly=yes '
    '-o UserKnownHostsFile=%s/.ssh/known_hosts -o StrictHostKeyChecking=no' % (WS, WS)))

MSG = """vn2: приёмная — Екатерина входит на описании, а не на приветствии

- Иван 2026-11-04: «появление Екатерины надо перенести на „Кудрявые седые как снег
  волосы, мягкое лицо“»
- CAST_ANCHOR: якорь приветствия заменён якорем описания (стр. 21 SCRIPT_CAST);
  на стр. 20 её ещё нет, на стр. 22 (приветствие) она уже в кадре
- _vn2_cg_range.py обновлён под новый выход: 10/10 (стр. 20 — только Сергей,
  стр. 21 — оба спрайта)
- регрессы ded_credits и auto_menu — зелёные, js-ошибок 0
"""

def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()

open(os.path.join(HERE, '.git_msg_kate_enter.txt'), 'w', encoding='utf-8').write(MSG)
print('add:', sh('git add -A')[0])
print('commit:', sh('git commit -q -F .git_msg_kate_enter.txt')[0])
print('HEAD:', sh('git log --oneline -1')[1][:110])
rc, out, err = sh('git push origin rebuild')
print('push rebuild rc=%d %s %s' % (rc, out[-160:], err[-200:]))
rc, out, err = sh('git push origin rebuild:master --force')
print('mirror master rc=%d %s %s' % (rc, out[-160:], err[-200:]))
