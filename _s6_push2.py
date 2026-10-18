# -*- coding: utf-8 -*-
"""Коммит + пуш: часы 06:07 убраны из S1 и S6."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))
MSG = ("VN эп1 (vn2): часы 06:07 убраны — S1 метка ПОДВОРОТНЯ без времени, S6 без плавающих "
       "часов (пробы диегетического LED-табло на будке оставлены в репе)")


def sh(cmd, t=600):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


add = ['_prolog_finals.py', 'assets/final/prolog/s1.png', 'assets/final/prolog/s6.png',
       'vn2/img/prolog/s1.webp', 'vn2/img/prolog/s6.webp', 'STATUS.md', 'PROLOG_FIXES.md',
       'assets/review/review_126_s6_noclock_vn.png',
       '_clock_led.py', '_s6_clock_ab.py', '_s6_clock_sheet.py', '_s6_clock_place.py',
       '_s6_clock_frame.py', '_s6_clock_f1.py', '_s6_c1_zoom.py', '_s6_c1_tight.py',
       '_s6_booth_edges.py', '_s6_booth_grid.py', '_s6_booth_low.py', '_s6_grid.py',
       '_s6_led_zoom.py', '_s6_v2_sheet.py', '_s6_v3_sheet.py',
       'assets/review/review_120_s6_clock_ab.png', 'assets/review/review_121_s6_clock.png',
       'assets/review/review_122_s6_clock_c1.png', 'assets/review/review_123_s6_clock_place.png',
       'assets/review/review_124_s6_clock_frame.png', 'assets/review/review_125_s6_clock_f1.png']
rc, out, err = sh('git add -A -- ' + ' '.join(add))
print('add:', rc, (out or err)[-200:])
print('commit:', sh('git commit -q -m "%s"' % MSG[:900])[:2])
rc, out, err = sh('git push origin HEAD:rebuild')
print('push:', rc, (out or err)[-300:])
print('HEAD:', sh('git log --oneline -1')[1][:130])
print('remote:', sh('git ls-remote --heads origin rebuild')[1])
