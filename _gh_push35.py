# -*- coding: utf-8 -*-
"""Пуш: живые проверки Pages (хеш s5 онлайн) + снимок онлайн-версии узла S5."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = ("VN эп1 (vn2): проверка живой демки — хеш vn2/img/prolog/s5.png на GitHub Pages "
       "совпал с локальным (_check_pages_s5, _wait_pages_s5), снимок онлайн-узла S5 review_98")

FILES = ['_check_pages_s5.py', '_wait_pages_s5.py', '_live_shot_s5.py',
         'assets/review/review_98_s5_live_pages.png']


def sh(cmd, t=1200):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


for f in FILES:
    sh('git add -- ' + repr(f))
print(sh("git diff --cached --stat")[1])
rc, out, err = sh('git commit -m ' + repr(MSG))
print("commit rc=", rc, (out or err)[-250:])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, (out or err)[-250:])
print("HEAD:", sh("git log --oneline -1")[1])
