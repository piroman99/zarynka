# -*- coding: utf-8 -*-
"""Коммит: кегль S4 подогнан под ширину ТВ (61 = 94% экрана) + пуш + живая проверка."""
import os
import hashlib
import subprocess
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))
MSG = ('VN эп1 (vn2): S4 — кегль подписи подогнан под ширину экрана ТВ (Иван: «слишком мелко»): '
       '52->42->61, ширина строки 861 px = 94% экрана ТВ (733..1650 в 2400x1350), '
       'плашка (738,684)-(1643,777) по центру экрана, 18 px под нижней кромкой; '
       'на наезде 1.5x текст 43 px и до подстрочника 101 px, в покое 29 px. '
       'Лист review_114_s4_caption_fit.png (было/покой/наезд), _vn2_restart.py 3/3 зелёный')


def sh(cmd, t=600):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


for f in ['_prolog_finals.py', 'assets/final/prolog/s4.png', 'vn2/img/prolog/s4.webp',
          'assets/review/review_113_s4_cap_wide.png', 'assets/review/review_113_s4_cap_zoom.png',
          'assets/review/review_114_s4_caption_fit.png', '_s4_cap_ab2.py', '_s4_cap_dom.py',
          '_s4_grid.py', '_s4_tv_box.py', '_s4_tv_edge.py']:
    rc, out, err = sh('git add -- ' + repr(f))
    if rc:
        print('add fail', f, (err or out)[-160:])
print('commit:', sh('git commit -m ' + repr(MSG))[1][-120:])
rc, out, err = sh('git push origin HEAD:rebuild')
print('push:', rc, (out or err)[-160:])
print('HEAD:', sh('git log --oneline -1')[1][:70])
print('remote:', sh('git ls-remote --heads origin rebuild')[1])
print('не закоммичено:', (sh("git status --short | grep -v '^??'")[1] or '(чисто)'))

local = open(os.path.join(HERE, 'vn2', 'img', 'prolog', 's4.webp'), 'rb').read()
url = 'https://piroman99.github.io/zarynka/vn2/img/prolog/s4.webp'
for i in range(8):
    try:
        req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache'})
        body = urllib.request.urlopen(req, timeout=30).read()
        same = hashlib.md5(body).hexdigest() == hashlib.md5(local).hexdigest()
        print('Pages попытка %d: %d B, совпал: %s' % (i + 1, len(body), same))
        if same:
            break
    except Exception as e:
        print('Pages ошибка:', e)
    time.sleep(20)
