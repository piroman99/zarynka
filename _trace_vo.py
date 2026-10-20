# -*- coding: utf-8 -*-
"""Трассировка одного файла озвучки: в каких коммитах менялись байты и что
про него говорил манифест (текст/голос/цена/reused_from)."""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
VO = 'vn2/audio/vo'
name = sys.argv[1] if len(sys.argv) > 1 else 'rec_23'
path = '%s/%s.mp3' % (VO, name)

def git(*a):
    return subprocess.run(['git'] + list(a), cwd=HERE, capture_output=True, text=True).stdout

commits = [c for c in git('log', '--format=%H %h %s').splitlines() if c]
for line in commits:
    h, short, subj = line.split(' ', 2)
    blob = git('rev-parse', '%s:%s' % (h, path)).strip()
    if not blob:
        continue
    man = {}
    raw = git('show', '%s:%s/_voices.json' % (h, VO))
    if raw:
        man = json.loads(raw).get(path) or {}
    print('%s %s  blob=%s  price=%s  voice=%-10s reused_from=%-14s text=%r'
          % (short, subj[:34], blob[:8], man.get('price'), man.get('voice'),
             man.get('reused_from'), (man.get('text') or '')[:60]))
