# -*- coding: utf-8 -*-
"""Пуш: пролог S1 — советская подворотня (мок + новая проба flux) + пересобранный аниматик."""
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
print("stat:", sh("git diff --cached --stat | tail -5")[1])
msg = ("Пролог S1: подворотня перерисована по-советски (облупленный кирпич, арка во двор, "
       "труба, лампочка на проводе, контейнеры, лужа, люк, силуэты в кепках); обновлена проба "
       "финала flux-2; аниматик пересобран (1:27.6). Лист review_57.")
rc, out, err = sh(f'git commit -m "{msg}" || true')
print("commit:", (out or err)[:400])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, out[-200:], "ERR:", err[-200:])
print("HEAD:", sh("git log --oneline -1")[1])
