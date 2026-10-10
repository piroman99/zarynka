# -*- coding: utf-8 -*-
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
def sh(cmd):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True)
    return (p.stdout or "") + (p.stderr or "")
# крупнейшие файлы, добавленные последним коммитом
out = sh("git show --stat --oneline HEAD | tail -n +2 | sort -t'|' -k2 -h | tail -25")
print(out[-3000:])
print("=== .tmp* в индексе ===")
print(sh("git ls-files | grep -E '^\\.tmp' | head -40"))
print("=== размер объектов ===")
print(sh("git count-objects -vH"))
