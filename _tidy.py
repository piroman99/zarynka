# -*- coding: utf-8 -*-
"""Убрать служебные файлы из git (следующим коммитом) и запушить."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.dirname(os.path.dirname(HERE))
KEY = os.path.join(WS, ".ssh", "github_ed25519")
KNOWN = os.path.join(WS, ".ssh", "known_hosts")
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    f"ssh -i {KEY} -o IdentitiesOnly=yes -o UserKnownHostsFile={KNOWN} "
    "-o StrictHostKeyChecking=no"))


def sh(cmd, t=600):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


# удалить из индекса и с диска разовые артефакты
for f in ("_commit_music.py", "out/_vert_check.png"):
    p = os.path.join(HERE, f)
    if os.path.exists(p):
        os.remove(p)
        print("removed:", f)

sh("git add -A")
print(sh("git diff --cached --stat")[1] or "(nothing staged)")
rc, out, err = sh('git commit -q -m "chore: убрать служебный скрипт и временный кадр" || true')
print("commit:", (out or err)[:160])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, (out or err)[-200:])
print("HEAD:", sh("git log --oneline -1")[1])
print("status:", sh("git status --short")[1] or "(clean)")
