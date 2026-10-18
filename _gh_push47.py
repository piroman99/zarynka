# -*- coding: utf-8 -*-
"""Пуш #2 после замены значка: живые проверки (файл на Pages + кадр в браузере)."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))


def sh(cmd, t=600):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


MSG = ('VN эп1 (vn2): живая проверка нового значка на Pages — out/znak3d_rot.mp4 отдаётся 200 '
       '(427 131 байт, совпал с локальным), content.js на Pages с новым путём, в браузере '
       'видео 1920x1080 / 5.4 с играет (снимок review_112)')

for f in ['_live_znak.py', '_live_znak_shot.py', 'assets/review/review_112_live_znak.png']:
    rc, out, err = sh('git add -- ' + repr(f))
    if rc:
        print('add fail', f, (err or out)[-160:])
print('commit:', sh('git commit -m ' + repr(MSG))[1][-200:])
rc, out, err = sh('git push origin rebuild')
print('push:', rc, (out or err)[-200:])
print('HEAD:', sh('git log --oneline -1')[1][:90])
print('remote:', sh('git ls-remote --heads origin rebuild')[1])
print('не закоммичено:', (sh("git status --short | grep -v '^??'")[1] or '(чисто)'))
