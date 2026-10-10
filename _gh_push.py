# -*- coding: utf-8 -*-
"""Коммит и пуш ветки rebuild в публичный GitHub-репозиторий piroman99/zarynka."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = "/home/ivan/.nanobot/workspace/.ssh/github_ed25519"
KH = "/home/ivan/.nanobot/workspace/.ssh/known_hosts"
REMOTE = "git@github.com:piroman99/zarynka.git"
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    f"ssh -i {KEY} -o IdentitiesOnly=yes -o UserKnownHostsFile={KH} "
    f"-o StrictHostKeyChecking=no"))


def sh(cmd, timeout=600):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=timeout, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


print("== secrets must be ignored ==")
rc, out, _ = sh("git check-ignore .pv_key && git ls-files | grep -c pv_key || true")
print(" check-ignore:", out)

print("== stage & commit ==")
print(" add:", sh("git add -A")[0])
rc, out, err = sh('git commit -m "rebuild: nano-banana consistency test + review sheets" || true')
print(" commit:", (out or err)[:200])

print("== remote ==")
rc, out, err = sh(f"git remote get-url origin 2>/dev/null || git remote add origin {REMOTE}")
print(" ", out, err)
print(" set-url:", sh(f"git remote set-url origin {REMOTE}")[0])
print(" ", sh("git remote -v")[1])

print("== ls-remote (до) ==")
print(sh("git ls-remote --heads origin")[1])

print("== PUSH rebuild ==")
rc, out, err = sh("git push -u origin rebuild", timeout=900)
print("rc=", rc)
print(out[-1500:])
print("ERR:", err[-1500:])

print("== ls-remote (после) ==")
print(sh("git ls-remote --heads origin")[1])
