# -*- coding: utf-8 -*-
"""Коммит и пуш: кадр p8 v4 (остекление) вставлен в пролог, старый S2 в архив."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = """vn2: пролог — кадр p8 «гидролаборатория» в сборке (корабль с остеклением)

- Иван: «Вариант B норм. Не нравится только что на межпланетном модуле нет иллюминаторов
  или лобовых стекол» — правка принятого кадра, а не новый кадр
- _prolog_p8_v4.py (gpt-image-2, 16:9 1K, 8.12 ₽ за A+B) с референсами
  prolog_p8v3_b + корабль из тизера: лента лобового остекления командного отсека
  (широкие трапециевидные окна, тёплый свет внутри) + ряд круглых иллюминаторов вдоль
  корпуса; выбран B (два ряда, корабль читается обитаемым)
- assets/final/prolog/p8.png = мастер prolog_p8v4_b
- старый кадр S2 (цех prologfin2_s2a) ушёл в assets/rejected/s2/ с записью в REJECTED.md:
  цех стал дублем нового p7, текст «Космонавты начали тренировки…» переехал на кадр
  гидролаборатории; узел s2 переименован в p8 (_p8_adopt.py)
- переозвучки НЕТ: s2_00.mp3 переименован в p8_00.mp3, манифест обновлён
- пролог: s1 → p6 → p7 → p8 → s3…s7, 13 страниц / 130.5 с, проблем 0
- регрессы зелёные: cg_range 10/10, ded_credits, restart 3/3, auto_menu"""

FILES = ['STATUS.md', '_vn2_build.py', '_voices_sync_prolog.py', '_vn2_vo_prolog_check.py',
         '_prolog_p8_v4.py', '_p8v4_sheet.py', '_p8v4_nose.py', '_p8v4_top.py',
         '_p8_adopt.py', '_p8_clean.py', '_shot_p8.py', '_p8_vn_sheet.py',
         '_push_p8v3.py', '_push_p8v4.py',
         'assets/final/prolog/p8.png',
         'assets/rejected/s2', 'assets/rejected/REJECTED.md',
         'assets/gen/prolog_p8v4_a__gpt-image-2_0.png',
         'assets/gen/prolog_p8v4_b__gpt-image-2_0.png',
         'vn2/content.js', 'vn2/img/prolog/p8.webp',
         'vn2/audio/vo/_voices.json', 'vn2/audio/vo/p8_00.mp3',
         '_sat/sheet_p8v4.png', '_sat/sheet_p8v4_detail.png',
         '_sat/sheet_p8v4_small.jpg', '_sat/sheet_p8v4_detail_small.jpg',
         '_sat/p8v4_nose.png', '_sat/p8v4_nose_small.jpg',
         '_sat/p8v4_top_A.jpg', '_sat/p8v4_top_B.jpg',
         '_sat/sheet_p8_vn.png', '_sat/sheet_p8_vn_small.jpg',
         '_sat/p8_p7_last.png', '_sat/p8_p8_p0.png', '_sat/p8_s3_p0.png']


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


with open(os.path.join(HERE, '.git_msg.txt'), 'w', encoding='utf-8') as f:
    f.write(MSG)

rc, out, err = sh('git add -A ' + ' '.join('"%s"' % f for f in FILES))
print('add rc', rc, err[-300:])
# удаления старых файлов тоже надо зафиксировать
sh('git add -A vn2/img/prolog vn2/audio/vo assets/final/prolog assets/rejected')
rc, out, err = sh('git -c user.name="nanobot" -c user.email="nanobot@karpoukhin.ru" '
                  'commit -q -F .git_msg.txt')
print('commit rc', rc, out[-200:], err[-400:])
print('HEAD', sh('git log --oneline -1')[1])
print('изменения в индексе:', sh('git status --porcelain | head -5')[1][:300])
rc, out, err = sh('git push origin rebuild')
print('push rc', rc, out[-300:], err[-400:])