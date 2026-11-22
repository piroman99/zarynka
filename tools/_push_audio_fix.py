# -*- coding: utf-8 -*-
"""Коммит правки музыки аллеи и пуш в feature-ветку rebuild (не master)."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    'ssh -i %s/.ssh/github_ed25519 -o IdentitiesOnly=yes '
    '-o UserKnownHostsFile=%s/.ssh/known_hosts -o StrictHostKeyChecking=no' % (WS, WS)))

ADD = [
    'vn2/content.js',
    '_vn2_build.py',
    'assets/audio/sketch/alley_mix.mp3',
    'assets/audio/sketch/alley_bed.mp3',
    'assets/audio/sketch/alley_amb.mp3',
    'assets/gen/poet_bench_neutral_0.png',
    '_alley_remix.py', '_alley_hf_check.py', '_music_loud_check.py', '_live_mp3_check.py',
    '_alley_fix3.py', '_alley_fix_check.py', '_push_alley_fix.py', '_pages_wait2.py',
    'assets/review', '_sat/sheet_alley_scene.png',
]


def run(args, **kw):
    r = subprocess.run(args, cwd=HERE, env=ENV, capture_output=True, text=True, **kw)
    if r.stdout.strip():
        print(r.stdout.strip()[-1500:])
    if r.returncode:
        print('!!', ' '.join(args), r.returncode, r.stderr[-800:])
    return r


run(['git', 'add'] + ADD)
st = run(['git', 'status', '--short'])
run(['git', 'commit', '-F', os.path.join(HERE, '.git_msg_audio.txt')])
run(['git', 'log', '--oneline', '-2'])
p = run(['git', 'push', 'origin', 'rebuild'])
print('push rc', p.returncode)
