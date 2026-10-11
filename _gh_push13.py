# -*- coding: utf-8 -*-
"""Пуш: смета пролога + раскадровка интро-медальона в piroman99/zarynka (ветка rebuild)."""
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


print("status:", sh("git status -sb")[1])
print("add:", sh("git add PROLOG_PLAN.md STATUS.md _medallion_board.py "
                "assets/review/review_25_medallion.png")[0])
rc, out, err = sh('git commit -m "PROLOG_PLAN: смета пролога (ролик/текст/гибрид) '
                  '+ концепты интро-медальона; раскадровка review_25" || true')
print("commit:", (out or err)[:300])
print("HEAD:", sh("git log --oneline -1")[1])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc)
print(out[-800:])
print("ERR:", err[-800:])
print("after:", sh("git status -sb")[1])
