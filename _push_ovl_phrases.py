# -*- coding: utf-8 -*-
"""Коммит и пуш в rebuild: строка надписи появляется на своей фразе (под озвучку)."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = """vn2: надписи кадров идут по фразам озвучки, а не все сразу

Иван: «буквы вываливаются слишком быстро; я думал под озвучку: "Марс — дело общее" —
буквы марс дело общее, нестройный хор — появляется "Общее", а что же обычных людей нет —
вместе с фразой». Первый вариант тянул буквы пропорционально ПЕЧАТИ подстрочника
(1.6 с на весь абзац), а озвучка s3 идёт 16.64 с — поэтому блок выскакивал сразу.

- _vn2_build.py: у строки появилась ФРАЗА ovl_t(..., at='подстрока текста'), ovl_at()
  переводит её в долю текста страницы (промах маркера = SystemExit); странице пишется
  vod — длительность её mp3 (ffmpeg, кеш на сборку).
  s3 at=[0.158, 0.158, 0.470, 0.693]/16.64 с; s4 [0.733]/8.15; s5a [0.28, 0.507]/7.08
  и [0, 0]/6.48; s5b [0.764]/10.03.
- vn2/app.js: часы титр-слоя — voice.currentTime/duration; fallback — печать подстрочника,
  затем ovlClock()/vod. ovlTick() (40 мс) стартует строку на её фразе и пишет буквами
  по LINE_MS (24 мс * PACE). Пауза P останавливает и буквы.
- Плашка теперь появляется вместе с первой строкой (fade), а не пустым прямоугольником.
- Новый тест-хук ?ovlp=P (прогресс страницы) для снимков и проверок; ?ovln=N остался.
- Проверки: _ovl_phrase_probe.py на реальном времени (s3 2.80/8.04/11.79 с, s5a 2.04/3.79,
  s4 6.05, s5b 7.78 — 0 проблем), _ovl_type.py через ?ovlp (0 проблем), _ovl_type_px.py
  (0 -> 11806 -> 14497 -> 16986 px на 0/20/50/75 %), лист _sat/ovl_phrases.png.
  Геометрия: _ovl_inside 0, _ovl_fit 0. Регрессы: _vn2_restart 3/3, _vn2_auto_menu."""

FILES = ['_vn2_build.py', 'vn2/app.js', 'vn2/content.js', 'STATUS.md',
         '_ovl_type.py', '_ovl_type_px.py', '_ovl_type_shots.py',
         '_ovl_phrase_probe.py', '_sat/ovl_phrases.png']


def sh(cmd, t=1200):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


with open(os.path.join(HERE, '.git_msg.txt'), 'w', encoding='utf-8') as f:
    f.write(MSG)

print('add rc', sh('git add ' + ' '.join('"%s"' % f for f in FILES))[0])
print(sh('git diff --cached --stat')[1])
print('commit rc', sh('git -c user.name="nanobot" -c user.email="nanobot@karpoukhin.ru" '
                     'commit -q -F .git_msg.txt')[0])
print('HEAD', sh('git log --oneline -1')[1])
if '--push' in os.sys.argv:
    rc, out, err = sh('git push origin rebuild')
    print('push rc', rc, out[-200:], err[-300:])
