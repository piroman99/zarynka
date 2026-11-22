import os, subprocess

WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEY = os.path.join(WS, '.ssh', 'github_ed25519')
KNOWN = os.path.join(WS, '.ssh', 'known_hosts')
env = dict(os.environ)
env['GIT_SSH_COMMAND'] = ('ssh -i %s -o IdentitiesOnly=yes -o UserKnownHostsFile=%s '
                          '-o StrictHostKeyChecking=no' % (KEY, KNOWN))

subprocess.run(['git', 'add', 'PROLOG_FIXES.md', 'STATUS.md', 'assets/rejected/s7',
                '_s7b_archive.py', '_s7b_sheet.py', '_s7b_check.py', '_s7b_live.py',
                '_s7b_map.py', '_s7b_map2.py', '_s7b_stats.py', '_s7b_wall.py',
                '_s7b_strip.py', '_s7b_strip2.py', '_zg_commons.py', '_zg_grab.py',
                '_zg_sheet.py', '_zg_osm.py', 'assets/review/review_130b_s7_vn_view.jpg'],
               capture_output=True, text=True)
r = subprocess.run(['git', 'commit', '-m',
                    'S7: archive rejected plates, document the new frame and plaque'],
                   capture_output=True, text=True)
print(r.stdout[-1200:], r.stderr[-500:])
r = subprocess.run(['git', 'push', 'origin', 'HEAD:rebuild'], capture_output=True, text=True, env=env)
print('push rc', r.returncode, r.stdout[-400:], r.stderr[-400:])
print(subprocess.run(['git', 'status', '--short'], capture_output=True, text=True).stdout[:800])
