# -*- coding: utf-8 -*-
"""Коммит оглавления в feature-ветку rebuild и пуш на GitHub.

Только файлы этой задачи: чужие правки (аллея, аудио, _sat) не трогаем —
они ждут слова Ивана.
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    'ssh -i %s/.ssh/github_ed25519 -o IdentitiesOnly=yes '
    '-o UserKnownHostsFile=%s/.ssh/known_hosts -o StrictHostKeyChecking=no' % (WS, WS)))

ADD = [
    'vn2/index.html', 'vn2/app.js', 'vn2/style.css',
    'STATUS.md',
    '_vn2_toc.py', '_vn2_toc_geom.py', '_toc_nodes.py', '_vn2_restart.py',
    '_push_toc.py', '.git_msg_toc.txt',
]


def run(args, **kw):
    r = subprocess.run(args, cwd=HERE, env=ENV, capture_output=True, text=True, **kw)
    if r.stdout.strip():
        print(r.stdout.strip()[-2000:])
    if r.returncode:
        print('!!', ' '.join(args), r.returncode, r.stderr[-800:])
    return r


run(['git', 'add'] + ADD)
run(['git', 'status', '--short'])
run(['git', 'commit', '-F', os.path.join(HERE, '.git_msg_toc.txt')])
run(['git', 'log', '--oneline', '-3'])
p = run(['git', 'push', 'origin', 'rebuild'])
print('push rebuild rc', p.returncode)
if p.returncode == 0:
    # зеркало master — только по слову Ивана; здесь его слово было «ок, делай. А»
    # (речь о варианте оглавления), зеркало НЕ трогаем.
    print('master НЕ трогаем (зеркало — только по отдельному слову)')
run(['git', 'rev-parse', '--short', 'HEAD'])
