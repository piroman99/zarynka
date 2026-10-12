# -*- coding: utf-8 -*-
"""Пуш: закадр пролога -> vn2/audio/*.mp3 (плейсхолдер, играет и на Pages)."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = "/home/ivan/.nanobot/workspace/.ssh/github_ed25519"
KH = "/home/ivan/.nanobot/workspace/.ssh/known_hosts"
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    f"ssh -i {KEY} -o IdentitiesOnly=yes -o UserKnownHostsFile={KH} "
    f"-o StrictHostKeyChecking=no"))

for junk in ("_vn2_vo.py",):
    p = os.path.join(HERE, junk)
    if os.path.exists(p):
        os.remove(p); print("removed", junk)


def sh(cmd, timeout=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=timeout, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


print("add rc:", sh("git add -A")[0])
print(sh("git diff --cached --stat | tail -12")[1])
msg = ("VN эп1: закадр пролога в vn2/audio/*.mp3 (моно 96k, ~0.9 МБ) — ПЛЕЙСХОЛДЕР ужатой "
       "версии клипа (vo_prolog2), играет и на GitHub Pages; content.js указывает на него. "
       "Дословный VO перезапишем после утверждения нарезки.")
rc, out, err = sh(f'git commit -m "{msg}" || true')
print("commit:", (out or err)[:300])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, out[-160:], "ERR:", err[-160:])
print("HEAD:", sh("git log --oneline -1")[1][:80])
print("status:", sh("git status --short")[1][:200])
