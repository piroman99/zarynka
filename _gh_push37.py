# -*- coding: utf-8 -*-
"""Пуш: проверка живой демки (предзагрузка на GitHub Pages) + gitignore на скретч-снимки."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = ("VN эп1 (vn2): живая проверка предзагрузки на Pages — 12 кадров/65 озвучек/2 видео в кэше, "
       "0 промахов, голос из blob, 0 ошибок JS (_live_preload.py, _wait_pages_app.py)")

FILES = ['_live_preload.py', '_wait_pages_app.py', '.gitignore', 'vn2/README.md']


def sh(cmd, t=1200):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


for f in FILES:
    sh('git add -- ' + repr(f))
print(sh("git diff --cached --stat")[1])
rc, out, err = sh('git commit -m ' + repr(MSG))
print("commit rc=", rc, (out or err)[-200:])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, (out or err)[-200:])
print("HEAD:", sh("git log --oneline -1")[1])
