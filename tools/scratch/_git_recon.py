# -*- coding: utf-8 -*-
"""Разведка: старый репозиторий zarynka + состояние локального гита проекта."""
import json, subprocess, urllib.request, os

def sh(cmd, cwd=None):
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=120)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()

print("== github api ==")
try:
    r = urllib.request.Request("https://api.github.com/repos/piroman99/zarynka",
                               headers={"User-Agent": "nanobot"})
    d = json.load(urllib.request.urlopen(r, timeout=30))
    for k in ("full_name", "private", "default_branch", "pushed_at", "created_at",
              "size", "fork", "forks_count", "stargazers_count"):
        print(f"  {k} = {d.get(k)}")
    print("  license =", (d.get("license") or {}).get("spdx_id"))
    print("  permissions =", d.get("permissions"))
except Exception as e:
    print("  ERR", e)

print("\n== branches ==")
print(sh("git ls-remote --heads https://github.com/piroman99/zarynka"))

print("\n== local project git ==")
print(sh("git rev-parse --show-toplevel", cwd="novella/zaryanka"))
print(sh("git status --short", cwd="novella/zaryanka")[0:2])

print("\n== workspace git tracked novella? ==")
print(sh("git ls-files novella/zaryanka", cwd=".")[0:2])
print("count:", sh("git ls-files novella/zaryanka", cwd=".")[1].count("\n") + 1)

print("\n== ssh keys present ==")
for p in ("/home/ivan/.nanobot/workspace/.ssh", "/home/ivan/.ssh"):
    print(" ", p, "->", sh(f"ls -la {p}")[1][:400] if os.path.exists(p) else "NO")
