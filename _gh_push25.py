# -*- coding: utf-8 -*-
"""Пуш: VN-эп1 «Пролог + Приёмная» — рабочая сборка vn2/ (движок + дословный текст + тумблеры)."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = "/home/ivan/.nanobot/workspace/.ssh/github_ed25519"
KH = "/home/ivan/.nanobot/workspace/.ssh/known_hosts"
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    f"ssh -i {KEY} -o IdentitiesOnly=yes -o UserKnownHostsFile={KH} "
    f"-o StrictHostKeyChecking=no"))

# устаревшие скриншоты первой итерации + одноразовые скрипты
for junk in ("_vn2_cleanup.py",
             "assets/review/review_70_vn2_kate_s.png",
             "assets/review/review_70_vn2_kate_sc.png",
             "assets/review/review_70_vn2_kate_sad.png",
             "assets/review/review_70_vn2_znak.png"):
    p = os.path.join(HERE, junk)
    if os.path.exists(p):
        os.remove(p); print("removed", junk)


def sh(cmd, timeout=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=timeout, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


print("add rc:", sh("git add -A")[0])
print(sh("git diff --cached --stat | tail -14")[1])
msg = ("VN эп1 (Пролог + Приёмная): рабочая сборка vn2/ — движок index/style/app, контент "
       "content.js (генератор _vn2_build.py); узлы титул -> значок-видео -> пролог S1..S7 "
       "(кадр-грейд + дословный текст + закадр) -> приёмная (фон + спрайты Сергей/Екатерина + "
       "дословный диалог). Независимые тумблеры текст/голос/музыка. Лист review_70.")
rc, out, err = sh(f'git commit -m "{msg}" || true')
print("commit:", (out or err)[:400])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, out[-200:], "ERR:", err[-200:])
print("HEAD:", sh("git log --oneline -1")[1])
print("status:", sh("git status --short")[1][:300])
