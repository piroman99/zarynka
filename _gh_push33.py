# -*- coding: utf-8 -*-
"""Пуш: (1) фикс показа S5 — скриншот снимался с node=5 (=S4), теперь node=6, лист review_96;
(2) бесплатные варианты размещения лозунга в S5 (лист review_97); (3) PV_MODELS.md — аудит моделей.
Коммитим только осмысленные файлы, мусорные пробы оставляем локально."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = ("VN эп1 (vn2): фикс показа S5 — скриншот снимался с node=5 (это S4), теперь node=6 "
       "(_vn_shot_node.py s1..s7|reception, review_96); бесплатные варианты лозунга S5 "
       "(A на фасаде / B и B2 лента на площади, review_97); PV_MODELS.md — аудит моделей PlusVibe")

FILES = [
    'PROLOG_FIXES.md', 'STATUS.md', 'PV_MODELS.md',
    '_s5_shot.py', '_vn_shot_node.py', '_prolog_s5_banner_ab.py',
    'assets/review/review_96_s5_vn_ok.png',
    'assets/review/review_97_s5_banner_ab.png',
    'assets/review/_s5_varA.png',
    'assets/review/_s5_varB.png',
    'assets/review/_s5_varB2.png',
]


def sh(cmd, t=1800):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


# убрать устаревший вариант C из первой попытки
stale = os.path.join(HERE, 'assets', 'review', '_s5_varC.png')
if os.path.exists(stale):
    os.remove(stale)
    print('удалён assets/review/_s5_varC.png')

print("HEAD до:", sh("git log --oneline -1")[1])
for f in FILES:
    rc, out, err = sh('git add -- ' + repr(f))
    if rc != 0:
        print('ADD FAIL', f, (out or err)[-200:])
print("в индексе:")
print(sh("git diff --cached --stat")[1])

rc, out, err = sh('git commit -m ' + repr(MSG))
print("commit rc=", rc, (out or err)[-400:])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, (out or err)[-400:])
print("HEAD:", sh("git log --oneline -1")[1])
print("не в индексе (остаётся локально):")
print(sh("git status --short")[1][:800])
