# -*- coding: utf-8 -*-
"""Коммит: озвучка сцены «аллея» (голос поэта — Umbriel).

Запуск: python3 _push_alley_vo.py
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    'ssh -i %s/.ssh/github_ed25519 -o IdentitiesOnly=yes '
    '-o UserKnownHostsFile=%s/.ssh/known_hosts -o StrictHostKeyChecking=no' % (WS, WS)))

MSG = """vn2: озвучка сцены «аллея у ворот» — голос поэта Umbriel

- Иван 2026-11-04 выбрал голос поэта: «2» из теста _voice_poet_test.py -> Umbriel
  (gemini-3.8-flash-tts, POET_STYLE: 25 лет, мягкий надломленный голос)
- записано 45 файлов al_00..al_40 (закадр 19, Екатерина 17, поэт 9), 14.88 ₽
- _vn2_vo_cast.py теперь озвучивает ВСЕ узлы с текстом (было жёстко reception) и
  берёт имена из pg.vof (план записи), а для переиспользования — только из pg.vo:
  план файла не значит, что файл есть
- VO_VER 6 -> 7 (иначе браузер и Pages отдают старый кэш mp3)
- проверки: _vo_sync_check 123/123, _vo_who_check 0 расхождений, _alley_vo_check 3/3
  (движок грузит al_00/al_04/al_14 без ошибок), пролог 130.3 с / 0 проблем
- регрессы: ded_credits, cg_range 10/10, auto_menu, start_mobile, restart 3/3 — зелёные
"""

def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()

open(os.path.join(HERE, '.git_msg_alley_vo.txt'), 'w', encoding='utf-8').write(MSG)
print('add:', sh('git add -A')[0])
print('commit:', sh('git commit -q -F .git_msg_alley_vo.txt')[0])
print('HEAD:', sh('git log --oneline -1')[1][:110])
rc, out, err = sh('git push origin rebuild')
print('push rebuild rc=%d %s %s' % (rc, out[-160:], err[-200:]))
rc, out, err = sh('git push origin rebuild:master --force')
print('mirror master rc=%d %s %s' % (rc, out[-160:], err[-200:]))
