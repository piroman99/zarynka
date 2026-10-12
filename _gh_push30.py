# -*- coding: utf-8 -*-
"""Пуш: спрайты/эмоции/каст + финальные кадры пролога S1..S7 (vn2). Всё «как есть»."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = ("VN эп1 (vn2): финальные кадры пролога S1..S7 (flux-2 + текстовый слой), "
       "эмоции/каст Сергея и Старика, кабинет-мок")


def sh(cmd, t=1800):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


print("HEAD до:", sh("git log --oneline -1")[1])
sh("git add -A")
rc, out, err = sh('git commit -m ' + repr(MSG))
print("commit rc=", rc, (out or err)[-400:])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, (out or err)[-400:])
print("HEAD:", sh("git log --oneline -1")[1])
print("ветка:", sh("git rev-parse --abbrev-ref HEAD")[1])
print("статус:", sh("git status --short")[1] or "(чисто)")
