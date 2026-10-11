# -*- coding: utf-8 -*-
"""Пуш: 3D-модель значка + интро-концепты + гравировка-пасхалка (piroman99/zarynka, rebuild)."""
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
print("status:", sh("git status -sb")[1][:400])

files = (
    "_znak3d.py _znak3d_check.py _znak3d_frames.py _znak3d_orient.py "
    "_znak3d_rib_macro.py _znak3d_rot.py _znak3d_rot_check.py _znak3d_rot_sheet.py "
    "_znak3d_texcheck.py "
    "_intro_k1.py _intro_k2.py _intro_k2b.py _intro_cmp.py "
    "_rib_eggs.py _rib_macro.py _k2b_ab.py _k2b_check.py _k2b_pixcheck.py "
    "_k2b_sheet.py _k2b_stills.py _znachek_nest_mock.py _net_probe.py "
    "_gh_push13.py _gh_push14.py "
    "PROLOG_PLAN.md STATUS.md "
    "assets/gen/znachek_k1.png assets/gen/znachek_k2_back.png"
)
print("add rc:", sh("git add " + files)[0])
# контрольные листы значка/интро
print("add sheets rc:", sh("git add assets/review/review_27_contest_full.png "
                          "assets/review/review_28_znachek_2x.png "
                          "assets/review/review_28_znachek_zoom.png "
                          "assets/review/review_29_znachek_pentagon.png "
                          "assets/review/review_30_pentagon_nest.png "
                          "assets/review/review_31_intro_k1.png "
                          "assets/review/review_31b_intro_k1_big.png "
                          "assets/review/review_32_intro_k2.png "
                          "assets/review/review_33_k1_vs_k2.png "
                          "assets/review/review_35_rib_eggs.png "
                          "assets/review/review_36_intro_k2b.png "
                          "assets/review/review_38_k2b_full.png "
                          "assets/review/review_46_znak3d_angles.png "
                          "assets/review/review_47_znak45.png "
                          "assets/review/review_48_rib90.png "
                          "assets/review/review_50_znak3d_rot_sheet.png "
                          "assets/review/review_52_rib90_macro.png")[0])
print("staged:", sh("git diff --cached --name-only")[1][:1200])
rc, out, err = sh('git commit -m "Значок: настоящая 3D-модель (пятиугольная призма, софт-рендер) '
                  '+ интро-концепты К1/К2/К2b + гравировка-пасхалка ЛМД на ребре" || true')
print("commit:", (out or err)[:300])
print("HEAD:", sh("git log --oneline -1")[1])
rc, out, err = sh("git push origin rebuild")
print("push rc=", rc)
print(out[-500:])
print("ERR:", err[-500:])
print("after:", sh("git status -sb")[1][:300])
