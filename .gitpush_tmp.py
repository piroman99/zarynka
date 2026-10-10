# -*- coding: utf-8 -*-
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))


def git(cmd):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, env=ENV)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


git("git add -A")
print("staged:", git("git status --short")[1])
print("commit:", git('git commit -m "VN: корневой редирект на vn/ для GitHub Pages" -q')[1] or "ok")
rc, out, err = git("git push origin rebuild")
print("push rc", rc, out, err)
print("remote:", git("git ls-remote origin rebuild")[1])
