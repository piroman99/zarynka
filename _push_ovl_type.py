# -*- coding: utf-8 -*-
"""Коммит и пуш в rebuild: буквы титр-слоя набираются вслед за подстрочником (вариант B)."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = """vn2: титр-слой кадров — буквы набираются по фразе (вариант B)

Раньше надпись кадра (pg.ovl) приходила на странице целиком и висела до конца фразы.
Теперь она проявляется по буквам тем же ритмом, что идёт подстрочник (решение Ивана
2026-11-04: «B конечно»).

- vn2/app.js: applyOvl() раскладывает строку на span'ы (пробелы — текстовые узлы,
  ширина и центровка строки не пляшут при наборе); ovlSync() вызывается из typeTick()
  и открывает floor(ty.i / tx.length * N) букв — надпись догоняет подстрочник и
  заканчивается вместе с ним. Пауза (P) останавливает набор.
- vn2/style.css: #ovl b span — opacity 0, span.in — тот же chIn (0.38 с), что и у
  подстрочника; #stage.paused останавливает анимацию; prefers-reduced-motion — сразу.
- ?letters=0 — без анимации (span.plain); ?instant=1 — тоже plain: под виртуальным
  временем Chrome CSS-анимация замирает на кадре opacity 0 и снимок выходил «без надписей».
- Новый тест-хук ?ovln=N — показать ровно N букв (снимки середины набора).
- Проверки: _ovl_type.py (DOM: 14→32 и 8→20 букв, к концу все, letters=0 сразу, 0 проблем);
  _ovl_type_px.py (пиксельно: s3 0→1891→5875→7205→8925 px при 0/5/13/26/47 буквах,
  чип s5b 118→734→1587 при 0/9/20); _ovl_type_shots.py → _sat/ovl_type.png (лист стадий);
  _ovl_dom_all.py — центры строк = центры плашек, 0 пустых слоёв (парсер процентов/span'ов).
- Регрессы: _vn2_restart 3/3, _vn2_auto_menu — зелёные."""

FILES = ['vn2/app.js', 'vn2/style.css', 'STATUS.md', '_ovl_dom_all.py',
         '_ovl_type.py', '_ovl_type_px.py', '_ovl_type_shots.py',
         '_live_ovl_type.py', '_sat/ovl_type.png']


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
if '--push' in os.sys.argv:
    rc, out, err = sh('git push origin rebuild')
    print('push rc', rc, out[-300:], err[-400:])
