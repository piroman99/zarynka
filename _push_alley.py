# -*- coding: utf-8 -*-
"""Коммит: сцена «аллея у ворот» (узлы steps + alley).

Запуск: python3 _push_alley.py
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    'ssh -i %s/.ssh/github_ed25519 -o IdentitiesOnly=yes '
    '-o UserKnownHostsFile=%s/.ssh/known_hosts -o StrictHostKeyChecking=no' % (WS, WS)))

MSG = """vn2: новая сцена «аллея у ворот» — ступени и скамейка у кованых ворот

- Иван 2026-11-04: «надо следующую сцену делать… но сначала фон» (после приёмной)
- два узла: steps (2 стр., «вышла из дверей… спустилась по широким ступеням») и
  alley (39 стр., «на скамейке между зелёных еловых лап сидел юноша»), текст дословный
  из assets/story.txt строки 71..121
- кадры: assets/gen/steps_a_0.png -> img/bg/steps, alley_b_0.jpg -> img/bg/alley
  (вариант B, ворота видны целиком; alley_a лежит рядом, замена — константа ALLEY_BG)
- узел steps идёт с trans=fade: перебивка на «* * *» перед выходом из приёмной
- _mk_pages() в сборке: разбивка тем же кодом, что приёмная; у страницы теперь vof
  (план озвучки) и vo (только существующие файлы) — иначе 404 в консоли
- каст по якорям: Екатерина sad -> neutral -> smile, поэт upset -> neutral -> interested;
  на последней странице Екатерина уходит ('-'), поэт остаётся один по центру
- _vn2_ded_credits.py больше не считает приёмную финалом: последний узел и его последняя
  страница берутся из content.js (было хардкодом node=reception&page=56)
- регрессы: cg_range 10/10, ded_credits, auto_menu, start_mobile, restart 3/3 — зелёные
"""

def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()

open(os.path.join(HERE, '.git_msg_alley.txt'), 'w', encoding='utf-8').write(MSG)
print('add:', sh('git add -A')[0])
print('commit:', sh('git commit -q -F .git_msg_alley.txt')[0])
print('HEAD:', sh('git log --oneline -1')[1][:110])
rc, out, err = sh('git push origin rebuild')
print('push rebuild rc=%d %s %s' % (rc, out[-160:], err[-200:]))
rc, out, err = sh('git push origin rebuild:master --force')
print('mirror master rc=%d %s %s' % (rc, out[-160:], err[-200:]))
