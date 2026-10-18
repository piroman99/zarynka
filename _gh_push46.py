# -*- coding: utf-8 -*-
"""Пуш: значок-видео пересобран в 1920x1080, вариант B (подпись ушла с жетона)."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


MSG = ('VN эп1 (vn2): значок-видео пересобран в 1920x1080 — вариант B, подпись ЗАРЯНКА ушла с жетона '
       '(зазор 142 px вместо наложения: титул впечён на y=120, а жетон занимал y 109..563). '
       'Текстуры граней 256->1024 (источник 1200, было растяжение 1.87x), суперсэмплинг 2x + LANCZOS '
       '(переход на ребре 48->3.4 px), альфа из z-буфера вместо вклеенного квадрата, кадр 1920x1080, '
       'вспышка ребра и ЛМД сохранены. build: _zn3d_hi.py -> _zn3d_build_B.py -> out/znak3d_rot.mp4 '
       '(черновик draft остаётся); content.js/_vn2_build.py переключены на финал, '
       'проверки _zn3d_swapcheck.py + _vn2_restart.py 3/3, снимки review_111; '
       '_live_mob.py синхронизирован с CSS (max-height:520px)')

FILES = [
    'out/znak3d_rot.mp4',
    'vn2/content.js', 'vn2/README.md', '_vn2_build.py', 'STATUS.md', '_live_mob.py',
    '_zn3d_hi.py', '_zn3d_build_B.py', '_zn3d_finalize.py', '_zn3d_verify.py',
    '_zn3d_swapcheck.py', '_zn3d_shots_after.py', '_zn3d_cleanup.py',
    'assets/review/review_109_znak_title.png',
    'assets/review/review_111_znak_desk_1600x900.png',
    'assets/review/review_111_znak_port_390x844.png',
    'assets/review/review_111_znak_land_844x390.png',
]
for f in FILES:
    rc, out, err = sh('git add -- ' + repr(f))
    if rc:
        print('add fail', f, (err or out)[-160:])

rc, out, err = sh('git commit -m ' + repr(MSG))
print('commit:', rc, (out or err)[-400:])
rc, out, err = sh('git push origin rebuild')
print('push:', rc, (out or err)[-300:])
print('HEAD:', sh('git log --oneline -1')[1])
print('remote:', sh('git ls-remote --heads origin rebuild')[1])
print('не закоммичено:', (sh("git status --short | grep -v '^??'")[1] or '(чисто)'))
