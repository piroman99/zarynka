# -*- coding: utf-8 -*-
"""Коммит и пуш: кадр p7 (цех сборки, недостроенная ракета) вставлен в пролог vn2."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = """vn2: пролог — кадр p7 «цех сборки» (новая генерация) в сборке

- Иван: «вставляем цех из новой генерации» — кадр prolog_p7_ceh_new (gpt-image-2,
  16:9 1K) встал в пролог между p6 и s2, мастер assets/final/prolog/p7.png
- текст L[7] разрезан ещё раз: «Но экспедиция потихоньку набиралась, модули корабля
  строились, финансирование приходило.» -> p7 (недостроенная ракета = модули строятся);
  «Космонавты начали тренировки, утверждалась научная программа…» -> s2
- индексы узлов сдвинулись: приёмная 12 -> 13 (p7 между p6 и s2)
- озвучка: p7_00 новый закадром Charon, s2_00 переозвучен под новый текст (0.50 ₽);
  манифест _voices.json синхронизирован; VO_VER 3 -> 4 (иначе браузер отдаёт старый s2_00)
- пролог целиком: 13 страниц / 130.5 с, проблем 0 (_vn2_vo_prolog_check)
- регрессы зелёные: cg_range 10/10, ded_credits, restart 3/3
- кадр p8 (бассейн) переделывается: Иван хочет футуристичный марсоподобный модуль
  и бассейн поглубже, старый «союзовский» макет не годится"""

FILES = ['STATUS.md', '_vn2_build.py',
         'assets/final/prolog/p7.png',
         'vn2/content.js', 'vn2/img/prolog/p7.webp',
         'vn2/audio/vo/_voices.json', 'vn2/audio/vo/p7_00.mp3',
         'vn2/audio/vo/s2_00.mp3',
         '_prolog_vo_p7.py', '_shot_p7.py', '_p7_vn_sheet.py',
         '_voices_sync_prolog.py', '_vn2_vo_prolog_check.py',
         '_prolog_678.py', '_prolog_678_sheet.py',
         '_vn2_cg_range.py', '_vn2_ded_credits.py', '_vn2_vo_check.py']


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
