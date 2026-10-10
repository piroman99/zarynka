# -*- coding: utf-8 -*-
"""прописать github.com в known_hosts и проверить аутентификацию ключом."""
import os, subprocess

KH = "/home/ivan/.nanobot/workspace/.ssh/known_hosts"
KEY = "/home/ivan/.nanobot/workspace/.ssh/github_ed25519"
SSH = (f'ssh -i {KEY} -o IdentitiesOnly=yes '
       f'-o StrictHostKeyChecking=no -o UserKnownHostsFile={KH}')


def sh(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    return (p.stdout or "").strip(), (p.stderr or "").strip()


out, err = sh(f"ssh-keyscan -T 15 github.com 2>/dev/null > {KH}.tmp && cat {KH} >> {KH}.tmp 2>/dev/null; "
              f"sort -u {KH}.tmp > {KH}; rm -f {KH}.tmp; wc -l {KH}")
print("known_hosts:", out, err)

out, err = sh(f"{SSH} -T git@github.com 2>&1")
print("\nauth:", out, "\n", err)
