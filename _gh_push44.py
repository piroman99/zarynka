# -*- coding: utf-8 -*-
"""Пуш: мобильная вёрстка vn2 (титул/кинозал во весь вьюпорт, портрет, полный экран, PWA)."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


MSG = ("VN эп1 (vn2): мобильная вёрстка — титул/кинозал/значок во весь вьюпорт "
       "(в портрете сцена 16:9 = полоса 219 px и «Тизер» обрезался), 100vh->100dvh, "
       "титул масштабируется под высоту, портрет: арт сверху + подстрочник снизу, "
       "кнопка «полный экран» + PWA-манифест (запуск с экрана Домой без адресной строки)")

files = ['vn2/app.js', 'vn2/index.html', 'vn2/style.css', 'vn2/manifest.webmanifest', 'vn2/sw.js',
         'STATUS.md',
         '_mob_probe.py', '_mob_qa.py', '_mob_func.py', '_mob_cap.py', '_mob_verify.py',
         '_sheet108.py', '_thumb.py', '_pl_miss.py', '_vn2_swap.py', '_desk_diff.py',
         'assets/review/review_108_mobile_fix.png']

for f in files:
    rc, out, err = sh('git add -- ' + repr(f))
    if rc:
        print("add fail", f, (err or out)[-160:])
rc, out, err = sh('git commit -m ' + repr(MSG))
print("commit:", rc, (out or err)[-400:])
rc, out, err = sh("git push origin rebuild")
print("push:", rc, (out or err)[-300:])
print("HEAD:", sh("git log --oneline -1")[1])
print("remote:", sh("git ls-remote --heads origin rebuild")[1])
print("не закоммичено:", (sh("git status --short | grep -v '^??'")[1] or "(чисто)"))
