# -*- coding: utf-8 -*-
"""Полная независимая проверка: куда реально ушёл пуш."""
import json, os, subprocess, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = "/home/ivan/.nanobot/workspace/.ssh/github_ed25519"
KH = "/home/ivan/.nanobot/workspace/.ssh/known_hosts"
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    f"ssh -i {KEY} -o IdentitiesOnly=yes -o UserKnownHostsFile={KH} -o StrictHostKeyChecking=no"))


def sh(cmd, cwd=HERE, t=120):
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=t, env=ENV)
    return (p.stdout or "").strip(), (p.stderr or "").strip()


print("== .git/config ==")
c, _ = sh("cat .git/config")
print(c)

print("\n== url rewrites (insteadOf) ==")
c, e = sh("git config --get-regexp '^url\\.' || echo '(нет)'")
print(c, e)

print("\n== кто я на github ==")
c, e = sh("ssh -i %s -o IdentitiesOnly=yes -o UserKnownHostsFile=%s -T git@github.com 2>&1" % (KEY, KH))
print(c)

print("\n== ls-remote origin (свежий) ==")
c, e = sh("git ls-remote origin")
print(c, "| err:", e[:200])

print("\n== local HEAD ==")
c, _ = sh("git rev-parse HEAD")
print(c)

print("\n== локальный лог (автор/даты) ==")
c, _ = sh("git log --pretty=format:'%h %ad %an <%ae> %s' --date=iso")
print(c)

print("\n== GitHub API: ветка rebuild ==")
for url in ("https://api.github.com/repos/piroman99/zarynka/branches/rebuild",
            "https://api.github.com/repos/piroman99/zarynka/commits?sha=rebuild&per_page=10"):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "nanobot"})
        d = json.load(urllib.request.urlopen(req, timeout=30))
        if isinstance(d, list):
            for cm in d:
                print("  ", cm["sha"][:10], cm["commit"]["author"]["date"], "|",
                      cm["commit"]["author"]["name"], "|", cm["commit"]["message"].splitlines()[0])
        else:
            print("  branch:", d.get("name"), "head:", (d.get("commit") or {}).get("sha", "")[:10],
                  "| protected:", d.get("protected"))
    except Exception as ex:
        print("  ERR", url, ex)
