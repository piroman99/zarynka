# -*- coding: utf-8 -*-
"""Пуш: предзагрузка кадров/голоса/видео в движке vn2 + тесты (_cdp.py, регрессия)."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = ("VN эп1 (vn2): предзагрузка в движке — очередь с приоритетами (4 потока) по списку "
       "из content.js, S1/значок вперёд, plWarm на 6 страниц вперёд, голос/музыка/видео "
       "через blob, полоса и % на титуле, «Начать» ждёт только критичное (клик — сразу); "
       "?preload=0 выключает; тесты _cdp.py + _pl_regress.py (листание = 0 запросов)")

# скретч-скрипт уборки не коммитим
junk = os.path.join(HERE, '_clean_pl.py')
if os.path.exists(junk):
    os.remove(junk)
    print('удалён _clean_pl.py')

FILES = ['vn2/app.js', 'vn2/index.html', 'vn2/style.css', 'vn2/README.md',
         '.gitignore', 'STATUS.md', 'PV_MODELS.md',
         '_cdp.py', '_pl_regress.py', '_pl_verify2.py', '_pl_slow.py', '_js_check.py',
         '_webp_estimate.py', 'assets/review/review_99_preload.png',
         'assets/review/review_96_s5_vn_ok.png']


def sh(cmd, t=1200):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


print("HEAD до:", sh("git log --oneline -1")[1])
for f in FILES:
    rc, out, err = sh('git add -- ' + repr(f))
    if rc:
        print('ADD FAIL', f, (out or err)[-160:])
print(sh("git diff --cached --stat")[1])
rc, out, err = sh('git commit -m ' + repr(MSG))
print("commit rc=", rc, (out or err)[-300:])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, (out or err)[-300:])
print("HEAD:", sh("git log --oneline -1")[1])
print("не закоммичено:", sh("git status --short")[1][:600] or '(чисто)')
