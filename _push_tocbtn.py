#!/usr/bin/env python3
"""Пуш ветки rebuild на GitHub: песочница требует GIT_SSH_COMMAND с абсолютным ключом."""
import os
import subprocess
import sys

WS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
REPO = os.path.dirname(os.path.abspath(__file__))
KEY = os.path.join(WS, ".ssh", "github_ed25519")
KNOWN = os.path.join(WS, ".ssh", "known_hosts")

env = dict(os.environ)
env["GIT_SSH_COMMAND"] = "ssh -i %s -o IdentitiesOnly=yes -o UserKnownHostsFile=%s -o StrictHostKeyChecking=yes" % (KEY, KNOWN)

print("HEAD:", subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                              capture_output=True, text=True).stdout.strip())
r = subprocess.run(["git", "push", "origin", "rebuild"], cwd=REPO, env=env,
                   capture_output=True, text=True)
print(r.stdout.strip()[-800:])
print(r.stderr.strip()[-800:])
print("rc =", r.returncode)
sys.exit(r.returncode)
