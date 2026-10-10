# -*- coding: utf-8 -*-
"""Перенести ключ GitHub в workspace/.ssh (я ошибся с путём)."""
import os, shutil, subprocess

WS = "/home/ivan/.nanobot/workspace"
src_dir = os.path.join(WS, "novella", ".ssh")
dst_dir = os.path.join(WS, ".ssh")
os.makedirs(dst_dir, exist_ok=True)
for n in ("github_ed25519", "github_ed25519.pub"):
    s, d = os.path.join(src_dir, n), os.path.join(dst_dir, n)
    if os.path.exists(s):
        shutil.move(s, d)
        print("moved", n)
os.chmod(os.path.join(dst_dir, "github_ed25519"), 0o600)
# убрать случайный каталог, если пуст
try:
    os.rmdir(src_dir)
except OSError:
    pass
print("\n== workspace/.ssh ==")
p = subprocess.run("ls -la", shell=True, cwd=dst_dir, capture_output=True, text=True)
print(p.stdout)
print("PUB:", open(os.path.join(dst_dir, "github_ed25519.pub")).read().strip())
