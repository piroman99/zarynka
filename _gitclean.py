# -*- coding: utf-8 -*-
"""Гигиена репозитория: не коммитить рабочие *.tmp* и _shots* каталоги."""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()

gi = os.path.join(HERE, ".gitignore")
txt = open(gi, encoding="utf-8").read()
txt = txt.replace(".tmp/\n.tmp_intro/\n", ".tmp*/\n_shots*/\n")
if ".tmp*/" not in txt:
    txt = txt.replace(".tmp/\n", ".tmp*/\n")
open(gi, "w", encoding="utf-8").write(txt)
print("--- .gitignore tmp-строки ---")
print("\n".join(l for l in txt.splitlines() if "tmp" in l or "shots" in l))

sh("git rm -r --cached .tmp_diag .tmp_intro3 .tmp_intro 2>/dev/null || true")
print("staged .tmp:", sh("git diff --cached --name-only | grep -c '.tmp'")[1])
sh("git add -A")
rc, out, err = sh('git commit -m "chore: рабочие .tmp* не коммитим (гигиена репозитория)" || true')
print("commit:", (out or err)[:180])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, (out or err)[-200:])
print("HEAD:", sh("git log --oneline -1")[1])
print("tracked .tmp:", sh("git ls-files | grep -c '^.tmp'")[1])
