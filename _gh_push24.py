# -*- coding: utf-8 -*-
"""Пуш: аниматик v4 (грейд «тёплый архив» + хвост S7 + затемнение после речи) + фикс дедлока ffmpeg."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = "/home/ivan/.nanobot/workspace/.ssh/github_ed25519"
KH = "/home/ivan/.nanobot/workspace/.ssh/known_hosts"
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    f"ssh -i {KEY} -o IdentitiesOnly=yes -o UserKnownHostsFile={KH} "
    f"-o StrictHostKeyChecking=no"))

for junk in ("_anim_watch.py", "_probe_dur.py"):
    p = os.path.join(HERE, junk)
    if os.path.exists(p):
        os.remove(p); print("removed", junk)


def sh(cmd, timeout=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=timeout, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


print("add rc:", sh("git add -A")[0])
print(sh("git diff --cached --stat | tail -12")[1])
msg = ("Пролог v4: грейд «тёплый архив»-lite (подтверждён) + ХВОСТ S7 «проходная·очередь» "
       "(10.4 c БЕЗ речи) + затемнение ПОСЛЕ речи; итог 1:37.98, 2450 кадров. Фикс дедлока "
       "ffmpeg (stderr в файл, -nostats) — рендер больше не встаёт на ~frame 2400. "
       "Листы review_68 (проверка), review_67 (пасхалка-героиня в очереди).")
rc, out, err = sh(f'git commit -m "{msg}" || true')
print("commit:", (out or err)[:400])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, out[-200:], "ERR:", err[-200:])
print("HEAD:", sh("git log --oneline -1")[1])
