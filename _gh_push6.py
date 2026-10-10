# -*- coding: utf-8 -*-
"""Коммит+пуш: космос-арт (партия 2) + AVM v3 (тёплая/эпичная музыка) + STATUS."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

def sh(cmd, t=1200):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()

print("check-ignore .pv_key:", sh("git check-ignore .pv_key")[1])
sh("git add -A")
print("staged:", sh("git diff --cached --stat | tail -3")[1])
rc, out, err = sh('git commit -m "rebuild: космос-арт партия 2 + AVM v3 (живые I2V-клипы, 2 музыкальных варианта)" || true')
print("commit:", (out or err)[:200])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, (out or err)[-220:])
print("HEAD:", sh("git log --oneline -1")[1], "| repo:", sh("du -sh .git | cut -f1")[1])
