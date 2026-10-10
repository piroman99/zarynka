# -*- coding: utf-8 -*-
"""Закоммитить и запушить музыку theme_epic_1 + журнал в github piroman99/zarynka (rebuild)."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.dirname(os.path.dirname(HERE))
KEY = os.path.join(WS, ".ssh", "github_ed25519")
KNOWN = os.path.join(WS, ".ssh", "known_hosts")
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    f"ssh -i {KEY} -o IdentitiesOnly=yes -o UserKnownHostsFile={KNOWN} "
    "-o StrictHostKeyChecking=no"))


def sh(cmd, t=1800):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


print("== branch ==", sh("git branch --show-current")[1])
print("\n== dirty ==")
print(sh("git status --short")[1] or "(clean)")

print("\n== size of tracked changes ==")
print(sh("git add -A && git diff --cached --stat | tail -12")[1])

msg = ("AVM: музыка эпичного тизера -> theme_epic_1.mp3 (выбор заказчика); "
       "пересборка 16:9 + 9:16, проверка review_23, журнал решений")
rc, out, err = sh(f'git commit -q -m "{msg}" || true')
print("\ncommit:", (out or err)[:200])

rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, (out or err)[-300:])
print("HEAD:", sh("git log --oneline -1")[1])
print("origin/rebuild:", sh("git rev-parse origin/rebuild")[1])
