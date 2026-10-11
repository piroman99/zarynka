# -*- coding: utf-8 -*-
"""Пуш: ракеты возвращены в S2 (космодром), аниматик пересобран."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = "/home/ivan/.nanobot/workspace/.ssh/github_ed25519"
KH = "/home/ivan/.nanobot/workspace/.ssh/known_hosts"
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    f"ssh -i {KEY} -o IdentitiesOnly=yes -o UserKnownHostsFile={KH} "
    f"-o StrictHostKeyChecking=no"))


def sh(cmd, timeout=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=timeout, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


print("add rc:", sh("git add -A")[0])
rc, out, err = sh("git diff --cached --stat | tail -2")
print("stat:", out)
rc, out, err = sh('git commit -m "Пролог S2: ракеты возвращены (космодром, ракета вертикально); аниматик пересобран" || true')
print("commit:", (out or err)[:300])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, out[-200:], "ERR:", err[-200:])
print("HEAD:", sh("git log --oneline -1")[1])
