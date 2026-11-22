# -*- coding: utf-8 -*-
"""Ключ для GitHub + проверка достижимости github.com."""
import os, subprocess

WS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../workspace
SSH = os.path.join(WS, ".ssh")
KEY = os.path.join(SSH, "github_ed25519")


def sh(cmd, cwd=WS):
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=60)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


os.makedirs(SSH, exist_ok=True)
if not os.path.exists(KEY):
    print(sh(f'ssh-keygen -t ed25519 -f "{KEY}" -N "" -C "nanobot-github"')[0:3])
os.chmod(KEY, 0o600)
print("\n== PUBLIC KEY (вставить в GitHub → SSH keys) ==")
print(open(KEY + ".pub").read().strip())
print("\n== reachability ==")
print("port22 :", sh("timeout 12 ssh -T -o StrictHostKeyChecking=no -o ConnectTimeout=10 git@github.com")[1:3])
print("443    :", sh("timeout 12 ssh -T -o StrictHostKeyChecking=no -o ConnectTimeout=10 -p 443 git@ssh.github.com")[1:3])
