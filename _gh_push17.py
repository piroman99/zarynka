# -*- coding: utf-8 -*-
"""Пуш пролога v2: голос без иронии, Звёздный городок без ракет, два варианта ролика."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = "/home/ivan/.nanobot/workspace/.ssh/github_ed25519"
KH = "/home/ivan/.nanobot/workspace/.ssh/known_hosts"
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    f"ssh -i {KEY} -o IdentitiesOnly=yes -o UserKnownHostsFile={KH} "
    f"-o StrictHostKeyChecking=no"))


def sh(cmd, timeout=1200):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=timeout, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


print("add rc:", sh("git add -A")[0])
rc, out, err = sh("git status --short")
print(out[:4000])
rc, out, err = sh("git diff --cached --stat | tail -3")
print("stat:", out)
rc, out, err = sh('git commit -m "Пролог: голос v2 без иронии (atempo 0.95), Звёздный городок без ракет, два ролика (голос/подстрочник)" || true')
print("commit:", (out or err)[:300])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc)
print(out[-400:], "ERR:", err[-400:])
print("HEAD:", sh("git log --oneline -1")[1])
