# -*- coding: utf-8 -*-
"""Мини-пуш: раздел «Источники спрайтов» в vn2/README.md."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = "/home/ivan/.nanobot/workspace/.ssh/github_ed25519"
KH = "/home/ivan/.nanobot/workspace/.ssh/known_hosts"
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    f"ssh -i {KEY} -o IdentitiesOnly=yes -o UserKnownHostsFile={KH} "
    f"-o StrictHostKeyChecking=no"))

def sh(cmd, timeout=600):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=timeout, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()

sh("git add -A")
print(sh("git diff --cached --stat")[1])
msg = "VN эп1: vn2/README — раздел «Источники спрайтов» (канон Сергей 42/flux-2, cutout)."
rc, out, err = sh(f'git commit -m "{msg}" || true')
print("commit:", (out or err)[:200])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, out[-140:], "ERR:", err[-140:])
print("HEAD:", sh("git log --oneline -1")[1][:80])
