# -*- coding: utf-8 -*-
"""Пуш: правка тизера «вариант A» (лого в круге, приёмная 16:9, тёмный градиент вместо blur-pad)."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()

MSG = ("Тизер: вариант A — логотип в круге (диск с альфой вместо белого квадрата), "
       "приёмная из готового 16:9 (комбинезон), blur-pad заменён тёмным градиентом; "
       "оба кадра (16:9 и 9:16) пересобраны на theme_epic_1, 29.92 с, 0 ₽")

files = ['build_avm_v3.py', 'out/avm_v3_epic.mp4', 'out/avm_v3_epic_9x16.mp4', 'STATUS.md',
         '_card_halo.py', '_teaser_check2.py', '_teaser_assets2.py', '_teaser_preview.py',
         '_logo_disc.py', '_logo_probe2.py', '_white_probe.py',
         'assets/review/review_106_teaser_fix_preview.png',
         'assets/review/review_107_teaser_fix_after.png']

for f in files:
    rc, out, err = sh('git add -- ' + repr(f))
    if rc:
        print("add fail", f, (err or out)[-160:])
rc, out, err = sh('git commit -m ' + repr(MSG))
print("commit:", rc, (out or err)[-300:])
rc, out, err = sh("git push origin rebuild")
print("push:", rc, (out or err)[-200:])
print("HEAD:", sh("git log --oneline -1")[1])
print("remote:", sh("git ls-remote --heads origin rebuild")[1])
print("не закоммичено:", (sh("git status --short | grep -v '^??'")[1] or "(чисто)"))
