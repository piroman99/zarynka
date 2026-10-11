# -*- coding: utf-8 -*-
"""Пуш: пасхалки v2 + гравировка (фикс rb_face, «ЛМД») + вкомпонованные в аниматик пасхалки."""
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
print("stat:", sh("git diff --cached --stat | tail -6")[1])
msg = ("Пасхалки пролога v2 (котобус S1 / транспорт №410 S2 / часы 06:07 S6) вкомпонованы в моки "
       "+ аниматик пересобран; гравировка ребра — фикс грани (RB_FACE=3), текст «ЛМД»; листы review_60..64.")
rc, out, err = sh(f'git commit -m "{msg}" || true')
print("commit:", (out or err)[:400])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, out[-200:], "ERR:", err[-200:])
print("HEAD:", sh("git log --oneline -1")[1])
