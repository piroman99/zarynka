#!/usr/bin/env python3
"""Пуш WIP-ветки аллеи (нужен GIT_SSH_COMMAND: в песочнице нет ~/.ssh/config)."""
import os
import subprocess
import sys

WS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
REPO = os.path.dirname(os.path.abspath(__file__))
KEY = os.path.join(WS, ".ssh", "github_ed25519")
KNOWN = os.path.join(WS, ".ssh", "known_hosts")

env = dict(os.environ)
env["GIT_SSH_COMMAND"] = ("ssh -i %s -o IdentitiesOnly=yes -o UserKnownHostsFile=%s "
                          "-o StrictHostKeyChecking=yes" % (KEY, KNOWN))
r = subprocess.run(["git", "push", "-u", "origin", "nanobot/alley-bench-angle"],
                   cwd=REPO, env=env, capture_output=True, text=True)
print(r.stdout.strip()[-600:])
print(r.stderr.strip()[-600:])
print("rc =", r.returncode)
sys.exit(r.returncode)
