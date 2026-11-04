# -*- coding: utf-8 -*-
"""Коммит: спрайт поэта (два вида, 6 эмоций) + он в кадре на отказе Лихнецкого.

Запуск: python3 _push_poet.py
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    'ssh -i %s/.ssh/github_ed25519 -o IdentitiesOnly=yes '
    '-o UserKnownHostsFile=%s/.ssh/known_hosts -o StrictHostKeyChecking=no' % (WS, WS)))

MSG = """vn2: спрайт поэта — два вида и шесть эмоций, он в кадре на отказе Лихнецкого

- Иван 2026-11-04: «надо его спрайты сделать, и потом вернуть этот спрайт в отказ
  лихнецкого в самом начале»; принят вариант v2-B (округлое лицо, лёгкая небритость,
  тёмные длинные волосы) после отказа от «аниме» v1
- канон 2016 (old:Sprites): «должен появляться в двух видах — с длинной плохой причёской
  и аккуратно стриженный»; эмоции: neutral/interested/upset и neutral/tired/inspired
- _poet_norm.py: крупность выровнена по ШИРИНЕ ПЛЕЧ (плечи/холст 0.56, у Сергея 0.559) —
  движок масштабирует спрайт по высоте, иначе при смене эмоции «прыгала» голова;
  файлы отдаются RGB на светло-сером фоне, вырезает их штатный cutout() сборки
- CAST_ANCHOR: добавлен уход спрайта ('-' вместо имени); поэт на стр. 0, ушёл на стр. 1
- _vn2_emo_verify.py был устаревшим (хардкод node=9, сверял скрытые img) — заменён
  на _vn2_emo_visible.py: 57/57 страниц показывают ровно заявленный файл эмоции
- регрессы cg_range 10/10, ded_credits, start_mobile — зелёные
"""

def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()

open(os.path.join(HERE, '.git_msg_poet.txt'), 'w', encoding='utf-8').write(MSG)
print('add:', sh('git add -A')[0])
print('commit:', sh('git commit -q -F .git_msg_poet.txt')[0])
print('HEAD:', sh('git log --oneline -1')[1][:110])
rc, out, err = sh('git push origin rebuild')
print('push rebuild rc=%d %s %s' % (rc, out[-160:], err[-200:]))
rc, out, err = sh('git push origin rebuild:master --force')
print('mirror master rc=%d %s %s' % (rc, out[-160:], err[-200:]))
