# -*- coding: utf-8 -*-
"""Пуш: раздача картинок переведена на WebP q92 (26.4 -> 3.9 МБ), оригиналы и мастера не тронуты."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = ("VN эп1 (vn2): раздача картинок -> WebP q92 (кадры 21->2.5 МБ, спрайты RGBA 4.9->0.37 МБ "
       "с альфой, vn2/img 26.4->3.9 МБ, предзагрузка 12.6->1.1 с); оригиналы assets/gen и "
       "мастера assets/final/prolog остаются PNG/JPEG без перекодирования; сверка review_100, "
       "рендер S5 MAE 1.08, регрессия 13/13")

FILES = ['_vn2_build.py', 'vn2/README.md', 'STATUS.md', '.gitignore',
         '_webp_ab.py', '_webp_alpha.py', '_webp_shots.py', '_webp_measure.py',
         '_webp_render_check.py',
         'assets/review/review_100_webp_ab.png',
         'assets/review/review_101_reception_webp.png',
         'assets/review/review_96_s5_vn_ok.png']
for n in ['s1', 's2', 's3', 's4', 's5', 's6', 's7']:
    FILES.append('vn2/img/prolog/%s.webp' % n)
for n in ['kate', 'kate_sad', 'sergey']:
    FILES.append('vn2/img/char/%s.webp' % n)
FILES.append('vn2/img/bg/reception.webp')


def sh(cmd, t=1200):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


print("HEAD до:", sh("git log --oneline -1")[1])
# добавляем всё нужное И удаления старых png/jpg в vn2/img
sh("git add -A -- vn2/img vn2/README.md")
for f in FILES:
    rc, out, err = sh('git add -- ' + repr(f))
    if rc:
        print('ADD FAIL', f, (out or err)[-160:])
print(sh("git diff --cached --stat")[1][:2000])
rc, out, err = sh('git commit -m ' + repr(MSG))
print("commit rc=", rc, (out or err)[-250:])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc, (out or err)[-250:])
print("HEAD:", sh("git log --oneline -1")[1])
print("не закоммичено:", (sh("git status --short")[1][:400] or '(чисто)'))
