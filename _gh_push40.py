# -*- coding: utf-8 -*-
"""Пуш: ожидание Pages по content.js + финальный отчёт."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))


def sh(cmd, t=600):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


for f in ['_wait_pages_content.py']:
    sh('git add -- ' + repr(f))
rc, out, err = sh('git commit -m ' + repr("VN эп1 (vn2): ожидание Pages по content.js — проверка, что демка отдаёт .webp"))
print("commit:", rc, (out or err)[-160:])
rc, out, err = sh("git push origin rebuild")
print("push:", rc, (out or err)[-160:])
print("HEAD:", sh("git log --oneline -1")[1])
print("remote:", sh("git ls-remote --heads origin rebuild")[1])
print("не закоммичено:", (sh("git status --short | grep -v '^??'")[1] or "(чисто)"))
