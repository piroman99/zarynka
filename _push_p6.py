# -*- coding: utf-8 -*-
"""Коммит и пуш: кадр p6 (хроника первого полёта, Марс) вставлен в пролог vn2."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = """vn2: пролог — кадр p6 «хроника первого полёта» (Марс) в сборке

- Иван: в хронике первого полёта нужны кадры С МАРСА, а не проводы на космодроме;
  выбран вариант B (средний план: двое в скафандрах идут по пыли, корабль силуэтом)
- _prolog_p6_mars.py (gpt-image-2, 16:9 1K, 5.40 ₽ за A+B), лист _prolog_p6_mars_sheet.py;
  вариант A ушёл в assets/rejected/p6/, прежний кадр-космодром — туда же
- текст L[7] разделён по смыслу: «Вторая Марсианская… Один раз были?» + «Ну и хорошо,
  гнаться за третьей…» уходят под кадр p6, «Но экспедиция потихоньку набиралась…» — под s2
- новый узел p6 встаёт между s1 и s2 (индексы узлов сдвинулись: приёмная 11 → 12)
- тесты больше не хардкодят номер узла: _vn2_nodes.node_index() читает content.js
  (_vn2_cg_range, _vn2_ded_credits)
- озвучка: p6_00/p6_01 закадром Charon, s2_00 переозвучен под новый текст,
  s2_01/s2_02 удалены; манифест _voices.json синхронизирован (_voices_sync_prolog.py)
- _vn2_vo_check починен: страницы-склейки (vo списком) больше не считаются ошибкой
- пролог целиком: 12 страниц / 130.4 с, файлов нет только у отсутствующих — 0 проблем
- регрессы зелёные: cg_range 10/10, ded_credits, restart 3/3, auto_menu"""

FILES = ['STATUS.md', '_vn2_build.py',
         'assets/final/prolog/p6.png',
         'assets/rejected/REJECTED.md', 'assets/rejected/p6',
         'vn2/content.js', 'vn2/img/prolog/p6.webp',
         'vn2/audio/vo/_voices.json', 'vn2/audio/vo/p6_00.mp3',
         'vn2/audio/vo/p6_01.mp3', 'vn2/audio/vo/s2_00.mp3',
         'vn2/audio/vo/s2_01.mp3', 'vn2/audio/vo/s2_02.mp3',
         '_prolog_p6_mars.py', '_prolog_p6_mars_sheet.py',
         '_prolog_678.py', '_prolog_678_sheet.py',
         '_prolog_vo_p6.py', '_prolog_vo_p6b.py', '_shot_p6.py',
         '_vn2_nodes.py', '_voices_sync_prolog.py', '_vn2_vo_prolog_check.py',
         '_p6_vn_sheet.py', '_archive_p6.py', '_archive_p6a.py',
         '_vn2_cg_range.py', '_vn2_ded_credits.py', '_vn2_vo_check.py',
         '_pages_check.py']


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


with open(os.path.join(HERE, '.git_msg.txt'), 'w', encoding='utf-8') as f:
    f.write(MSG)

rc, out, err = sh('git add -A ' + ' '.join('"%s"' % f for f in FILES))
print('add rc', rc, out[-300:], err[-300:])
rc, out, err = sh('git -c user.name="nanobot" -c user.email="nanobot@karpoukhin.ru" '
                  'commit -q -F .git_msg.txt')
print('commit rc', rc, out[-300:], err[-400:])
print('HEAD', sh('git log --oneline -1')[1])
print('status', sh('git status --porcelain -- ' + ' '.join('"%s"' % f for f in FILES))[1][:300])
rc, out, err = sh('git push origin rebuild')
print('push rc', rc, out[-300:], err[-400:])
