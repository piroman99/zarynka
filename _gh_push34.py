# -*- coding: utf-8 -*-
"""Пуш: S5 закрыт окончательно — вариант A лозунга перенесён в сборку, vn2 пересобран."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = ("VN эп1 (vn2): S5 закрыт окончательно — заказчик выбрал вариант A лозунга "
       "(полоса на фасаде, кегли 76/62, чип «2 МЕСТА С УЛИЦЫ»); перенесено в _prolog_finals.py, "
       "vn2 пересобран 0 руб, S1-S4/S6/S7 байт-в-байт, скриншот review_96")

FILES = ['_prolog_finals.py', 'PROLOG_FIXES.md',
         'assets/final/prolog/s5.png', 'vn2/img/prolog/s5.png',
         'assets/review/review_96_s5_vn_ok.png']


def sh(cmd, t=1800):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


print("HEAD до:", sh("git log --oneline -1")[1])
for f in FILES:
    sh('git add -- ' + repr(f))
print(sh("git diff --cached --stat")[1])
rc, out, err = sh('git commit -m ' + repr(MSG))
print("commit rc=", rc, (out or err)[-300:])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, (out or err)[-300:])
print("HEAD:", sh("git log --oneline -1")[1])
print("изменённые файлы (не закоммичено):", sh("git status --short | grep -v '^??'")[1] or "(нет)")
