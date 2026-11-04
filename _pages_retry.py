# -*- coding: utf-8 -*-
"""Перезапуск деплоя Pages пустым коммитом.

Причина падения ba55d03: шаг «Deploy to GitHub Pages» упёрся в 10-минутный лимит
(старт 21:58:59, failure 22:09:38 ≈ 640 с) — это таймаут GitHub, а не ошибка сборки
(job build = success). Лечится повтором: пустой коммит в rebuild запускает новый деплой.
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    'ssh -i %s/.ssh/github_ed25519 -o IdentitiesOnly=yes '
    '-o UserKnownHostsFile=%s/.ssh/known_hosts -o StrictHostKeyChecking=no' % (WS, WS)))


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


print('commit:', sh('git commit --allow-empty -m "chore: повторный деплой Pages '
                    '(предыдущий упёрся в 10-минутный лимит)"')[0])
print('HEAD:', sh('git log --oneline -1')[1][:100])
rc, out, err = sh('git push origin rebuild')
print('push rebuild rc=%d %s %s' % (rc, out[-140:], err[-160:]))
rc, out, err = sh('git push origin rebuild:master --force')
print('mirror master rc=%d %s %s' % (rc, out[-140:], err[-160:]))
