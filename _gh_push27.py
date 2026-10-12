# -*- coding: utf-8 -*-
"""Пуш: канон Сергея 42 (flux-2) + вырезка фона спрайтов (cutout) + доки."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = "/home/ivan/.nanobot/workspace/.ssh/github_ed25519"
KH = "/home/ivan/.nanobot/workspace/.ssh/known_hosts"
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    f"ssh -i {KEY} -o IdentitiesOnly=yes -o UserKnownHostsFile={KH} "
    f"-o StrictHostKeyChecking=no"))

for junk in ("_cutout_num.py", "_sergey_chk.py"):
    p = os.path.join(HERE, junk)
    if os.path.exists(p):
        os.remove(p); print("removed", junk)

def sh(cmd, timeout=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=timeout, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()

print("add rc:", sh("git add -A")[0])
print(sh("git diff --cached --stat | tail -15")[1])
msg = ("VN эп1: канон Сергея = 42 года (sergey_eng_old, выбран flux-2) + вырезка фона спрайтов "
       "(cutout в _vn2_build.py: flood-fill от бордюра; фон генератора не всегда белый). "
       "Доки README/VN_PLAN/STATUS приведены к канону 42. Листы review_71/72/73.")
rc, out, err = sh(f'git commit -m "{msg}" || true')
print("commit:", (out or err)[:300])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, out[-160:], "ERR:", err[-160:])
print("HEAD:", sh("git log --oneline -1")[1][:90])
print("status:", sh("git status --short")[1][:240])
