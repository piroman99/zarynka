import os, subprocess

WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEY = os.path.join(WS, '.ssh', 'github_ed25519')
KNOWN = os.path.join(WS, '.ssh', 'known_hosts')
env = dict(os.environ)
env['GIT_SSH_COMMAND'] = ('ssh -i %s -o IdentitiesOnly=yes -o UserKnownHostsFile=%s '
                          '-o StrictHostKeyChecking=no' % (KEY, KNOWN))
subprocess.run(['git', 'add', 'PROLOG_FIXES.md', 'STATUS.md'], capture_output=True, text=True)
r = subprocess.run(['git', 'commit', '-m', 'S7: document the quiet plaque variant'],
                   capture_output=True, text=True)
print(r.stdout[-400:], r.stderr[-300:])
r = subprocess.run(['git', 'push', 'origin', 'HEAD:rebuild'], capture_output=True, text=True, env=env)
print('push rc', r.returncode, r.stdout[-200:], r.stderr[-200:])
