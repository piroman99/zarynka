# -*- coding: utf-8 -*-
"""Сверка: локальный HEAD == удалённая ветка rebuild; оба mp4 действительно в коммите."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))


def sh(cmd, t=300):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


print("local HEAD :", sh("git rev-parse HEAD")[1])
print("remote     :", sh("git ls-remote --heads origin rebuild")[1])
print("ahead/behind:", sh("git rev-list --left-right --count HEAD...origin/rebuild")[1])
print()
print("файлы в коммите:")
for line in sh("git show --stat --oneline HEAD")[1].splitlines():
    if "avm_v3_epic" in line or "build_avm" in line:
        print("  ", line.strip())
print()
print("размеры в репо (git cat-file):")
for f in ("out/avm_v3_epic.mp4", "out/avm_v3_epic_9x16.mp4"):
    print("  ", f, sh("git cat-file -s HEAD:" + f)[1], "B")
