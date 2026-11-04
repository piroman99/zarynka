# -*- coding: utf-8 -*-
"""Докоммит: живая проверка демо s1/p6 (STATUS.md + новые проверочные скрипты).

Запуск: python3 _push_s1p6_live.py
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


print('add:', sh('git add STATUS.md _live_s1p6.py _pages_wait_s1p6.py '
                 '_pages_status.py _pages_deploy_status.py _probe_404_s1.py')[0])
print('commit:', sh('git commit -q -m "vn2: пролог — живая проверка кадров s1/p6 на демо"')[0])
print('HEAD:', sh('git log --oneline -1')[1][:110])
rc, out, err = sh('git push origin rebuild')
print('push rebuild rc=%d %s %s' % (rc, out[-160:], err[-200:]))
rc, out, err = sh('git push origin rebuild:master --force')
print('mirror master rc=%d %s %s' % (rc, out[-160:], err[-200:]))
