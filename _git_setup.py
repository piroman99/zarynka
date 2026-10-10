# -*- coding: utf-8 -*-
"""Локальная версионизация проекта «Зарянка» → ветка rebuild (пуш вручную, не отсюда)."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def sh(cmd):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True, timeout=300)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


if not os.path.exists(os.path.join(HERE, ".git")):
    print("init:", sh("git init -b rebuild")[0:3])
    print("cfg name:", sh('git config user.name "Ivan Karpukhin"')[2] or "ok")
    print("cfg mail:", sh('git config user.email "piroman99@yandex.ru"')[2] or "ok")
    print("cfg quotepath:", sh("git config core.quotepath false")[2] or "ok")

print("add:", sh("git add -A")[0])
rc, out, err = sh('git commit -m "Зарянка: реконструкция VN — сценарий, промпты, стиль flux-2, кадры"')
print("commit rc=", rc, "|", (out or err)[:400])

print("\n== status ==")
print(sh("git status --short | head -20")[1])
print("\n== files tracked ==")
rc, out, _ = sh("git ls-files | wc -l")
print("count:", out)
rc, out, _ = sh("git ls-files")
for f in out.splitlines():
    print("  ", f)
print("\n== repo size (MB) ==")
rc, out, _ = sh("du -sh .git | cut -f1")
print(out)
