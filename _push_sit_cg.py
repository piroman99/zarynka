# -*- coding: utf-8 -*-
"""Коммит: сидящий поэт (3 эмоции) + CG «Муза».

Запуск: python3 _push_sit_cg.py
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    'ssh -i %s/.ssh/github_ed25519 -o IdentitiesOnly=yes '
    '-o UserKnownHostsFile=%s/.ssh/known_hosts -o StrictHostKeyChecking=no' % (WS, WS)))

MSG = """vn2: сцена «аллея» — сидящий поэт и CG «Муза»

- Иван 2026-11-04: «1.B 2.B. Давай попробуем CG на музу» (кадр аллеи остаётся B)
- сидящий поэт: 3 эмоции (upset / neutral / interested), генератор _poet_sit.py,
  референс лица — принятый poet2_b_0.png; матирование и нормировка _poet_sit_norm.py
  (плечи/холст 0.60 — сидящая фигура законно шире стоячего каста 0.56)
- в сборке отдельный ключ персонажа 'Поэт (сидя)' -> poet_sit*.png; сцена «аллея»
  использует его, приёмная остаётся со стоящим 'Поэт'
- CG «Муза» (cg_muza, 4.06 ₽): акварель, референсы — кадр аллеи (место), спрайт поэта
  и спрайт Екатерины (лица); стоит фоном на странице «— Муза, — юноша покраснел и
  отвернулся», спрайты внутри диапазона убраны
- готча: _anchor2 считает по всему raw2, а alley_pages = raw2[_cut2:] — индекс CG
  надо сдвигать на _cut2 (иначе кадр встал на «Держите…» вместо «Муза»)
- регрессы: ded_credits, cg_range 10/10 — зелёные
"""

def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()

open(os.path.join(HERE, '.git_msg_sit_cg.txt'), 'w', encoding='utf-8').write(MSG)
print('add:', sh('git add -A')[0])
print('commit:', sh('git commit -q -F .git_msg_sit_cg.txt')[0])
print('HEAD:', sh('git log --oneline -1')[1][:110])
rc, out, err = sh('git push origin rebuild')
print('push rebuild rc=%d %s %s' % (rc, out[-160:], err[-200:]))
rc, out, err = sh('git push origin rebuild:master --force')
print('mirror master rc=%d %s %s' % (rc, out[-160:], err[-200:]))
