# -*- coding: utf-8 -*-
"""Пуш: гравировка «МЕЛЬКОМ» (без паузы на рёбре) + предложенный кадр S7 «ПРОХОДНАЯ·ОЧЕРЕДЬ».
Заодно убирает одноразовые probe-скрипты, чтобы не мусорить в дереве."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = "/home/ivan/.nanobot/workspace/.ssh/github_ed25519"
KH = "/home/ivan/.nanobot/workspace/.ssh/known_hosts"
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    f"ssh -i {KEY} -o IdentitiesOnly=yes -o UserKnownHostsFile={KH} "
    f"-o StrictHostKeyChecking=no"))

# throwaway probes — не храним
for junk in ("_stat_probe.py", "_dur_probe.py"):
    p = os.path.join(HERE, junk)
    if os.path.exists(p):
        os.remove(p)
        print("removed", junk)


def sh(cmd, timeout=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=timeout, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


print("add rc:", sh("git add -A")[0])
print("stat:\n" + sh("git diff --cached --stat | tail -10")[1])
msg = ("Пролог: гравировка ребра «МЕЛЬКОМ» (убрана пауза на 90°, сплошной проход 0.6–2.3 c, "
       "«ЛМД» видно 1–2 кадра) — флейш-лист review_66; предложен новый кадр S7 «ПРОХОДНАЯ·ОЧЕРЕДЬ» "
       "(мок + лист review_65, ждём решения); аниматик пересобран (1:27.6).")
rc, out, err = sh(f'git commit -m "{msg}" || true')
print("commit:", (out or err)[:400])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, out[-200:], "ERR:", err[-200:])
print("HEAD:", sh("git log --oneline -1")[1])
