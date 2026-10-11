# -*- coding: utf-8 -*-
"""Пуш: заметка о конкурсе иллюстраций (2061.su) + скрипты в piroman99/zarynka (rebuild)."""
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


print("branch:", sh("git rev-parse --abbrev-ref HEAD")[1])
print("status:", sh("git status -sb")[1][:500])
files = ("CONTEST.md .gitignore _2061_harvest.py _2061_scenemap.py "
         "_contest_sheet.py _contest_ranged.py _contest_audit.py _contest_audit2.py "
         "_contest_trunc.py _contest_headers.py _contest_refetch.py")
print("add rc:", sh("git add " + files)[0])
print("staged:", sh("git diff --cached --name-only")[1])
rc, out, err = sh('git commit -m "CONTEST.md: конкурс иллюстраций «Зарянка» (2061.su) — '
                  'итоги, карта сцен, референс-библиотека; фикс обрезки загрузки (Range-чанки)" || true')
print("commit:", (out or err)[:300])
print("HEAD:", sh("git log --oneline -1")[1])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc)
print(out[-600:])
print("ERR:", err[-600:])
print("after:", sh("git status -sb")[1][:300])
