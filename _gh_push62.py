# -*- coding: utf-8 -*-
"""Коммит и пуш фикса: «Начать» больше не уезжает вправо от логотипа."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

MSG = """vn2: logo is a block again — «Начать» stays under it

Without the title lines the logo <img> and the «Начать» <button> are both
inline-level, so they shared one line and the button drifted to the right of
the logo (seen by Ivan on the start screen). The logo is now display:block
with auto margins, so the button, the loading bar and «Тизер» are always
centred under it in both modes (with and without titles) and in portrait.

Measured: notitles 1280x720 — logo cy 278, «Начать» cy 421 cx 640 (was 740),
bar 456, teaser 495; portrait 390x844 all centred at cx 195.
_vn2_start_mobile.py 17/17 green.
"""


def sh(cmd, t=600):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


open(os.path.join(HERE, '.git_msg.txt'), 'w').write(MSG)
print('add:', sh('git add vn2/style.css .git_msg.txt _title_measure.py')[0])
print('commit:', sh('git commit -q -F .git_msg.txt')[0])
print('rm-cached:', sh('git rm -q --cached .git_msg.txt')[0])
print('commit2:', sh('git commit -q -m "chore: drop the temporary commit message file"')[0])
print('push rebuild:', sh('git push origin rebuild')[1][-300:])
print('mirror master:', sh('git push origin rebuild:master --force')[1][-300:])
print('HEAD:', sh('git log --oneline -1')[1][:100])
print('status:', (sh("git status --short | grep -v '^??'")[1] or '(чисто)'))
