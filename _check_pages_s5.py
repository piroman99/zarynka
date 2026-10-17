# -*- coding: utf-8 -*-
"""Проверка: (1) что remote rebuild = локальный HEAD; (2) что GitHub Pages уже отдаёт НОВЫЙ s5."""
import os, subprocess, hashlib, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    "ssh -i /home/ivan/.nanobot/workspace/.ssh/github_ed25519 -o IdentitiesOnly=yes "
    "-o UserKnownHostsFile=/home/ivan/.nanobot/workspace/.ssh/known_hosts "
    "-o StrictHostKeyChecking=no"))

r = subprocess.run(['git', 'ls-remote', '--heads', 'origin', 'rebuild'],
                   cwd=HERE, capture_output=True, text=True, env=ENV, timeout=120)
print('remote rebuild:', (r.stdout or r.stderr).strip())
loc = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=HERE, capture_output=True, text=True)
print('local HEAD     :', loc.stdout.strip())


def sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


local = open(os.path.join(HERE, 'vn2', 'img', 'prolog', 's5.png'), 'rb').read()
print('local  vn2/img/prolog/s5.png', len(local), sha(local))

url = 'https://piroman99.github.io/zarynka/vn2/img/prolog/s5.png'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'nanobot', 'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = resp.read()
    print('pages  ', len(data), sha(data), '->', 'СОВПАДАЕТ (новый кадр онлайн)' if sha(data) == sha(local) else 'СТАРЫЙ кадр (CDN ещё не обновился)')
except Exception as e:
    print('pages fetch FAIL:', type(e).__name__, e)
