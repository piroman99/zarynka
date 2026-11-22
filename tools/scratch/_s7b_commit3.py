import os, subprocess

WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEY = os.path.join(WS, '.ssh', 'github_ed25519')
KNOWN = os.path.join(WS, '.ssh', 'known_hosts')
env = dict(os.environ)
env['GIT_SSH_COMMAND'] = ('ssh -i %s -o IdentitiesOnly=yes -o UserKnownHostsFile=%s '
                          '-o StrictHostKeyChecking=no' % (KEY, KNOWN))

print(subprocess.run(['git', 'add', '-u', 'assets/gen'], capture_output=True, text=True).stdout)
print(subprocess.run(['git', 'status', '--short', 'assets/gen', 'assets/rejected'],
                     capture_output=True, text=True).stdout)
r = subprocess.run(['git', 'commit', '-m', 'S7: drop the archived plate from assets/gen (moved to rejected)'],
                   capture_output=True, text=True)
print(r.stdout[-600:], r.stderr[-400:])
r = subprocess.run(['git', 'push', 'origin', 'HEAD:rebuild'], capture_output=True, text=True, env=env)
print('push rc', r.returncode, r.stdout[-300:], r.stderr[-300:])
print(subprocess.run(['git', 'log', '--oneline', '-3'], capture_output=True, text=True).stdout)
