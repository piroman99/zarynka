# -*- coding: utf-8 -*-
import subprocess, os
REPO = "/home/ivan/.nanobot/workspace/novella/zaryanka"
def run(a):
    r = subprocess.run(a, cwd=REPO, capture_output=True, text=True)
    return r.stdout + r.stderr

print("== branches")
print(run(["git","branch","-a"]))
print("== old tree (top)")
print(run(["git","ls-tree","-r","--name-only","old"])[:4000])
