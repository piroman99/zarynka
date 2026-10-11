# -*- coding: utf-8 -*-
"""Пуш: обновление журналов (STATUS/PROLOG_PLAN) после одобрения 3D-значка."""
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


print("add rc:", sh("git add STATUS.md PROLOG_PLAN.md")[0])
print("staged:", sh("git diff --cached --name-only")[1])
rc, out, err = sh('git commit -m "Значок 3D одобрен заказчиком; пауза на ребре 0.35 с; зеркало — идея пасхалки" || true')
print("commit:", (out or err)[:240])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc)
print(out[-300:], "ERR:", err[-300:])
print("HEAD:", sh("git log --oneline -1")[1])
