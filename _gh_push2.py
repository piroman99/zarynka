# -*- coding: utf-8 -*-
"""Коммит+пуш новых артефактов (лист персонажа, серия 5 сцен)."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


print("secrets ok:", sh("git check-ignore .pv_key")[1])
sh("git add -A")
rc, out, err = sh('git commit -m "rebuild: лист персонажа + серия 5 сцен (nano-banana-2.1)" || true')
print("commit:", (out or err)[:200])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc)
print((out or err)[-600:])
print("HEAD:", sh("git log --oneline -1")[1])
