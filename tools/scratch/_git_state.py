import os, subprocess

WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEY = os.path.join(WS, '.ssh', 'github_ed25519')
KNOWN = os.path.join(WS, '.ssh', 'known_hosts')
env = dict(os.environ)
env['GIT_SSH_COMMAND'] = ('ssh -i %s -o IdentitiesOnly=yes -o UserKnownHostsFile=%s '
                          '-o StrictHostKeyChecking=no' % (KEY, KNOWN))

def run(*a):
    r = subprocess.run(list(a), capture_output=True, text=True, env=env)
    print('$', ' '.join(a), '-> rc', r.returncode)
    print(r.stdout.strip()[:1500])
    if r.stderr.strip():
        print('ERR:', r.stderr.strip()[:600])

run('git', 'ls-remote', '--heads', 'origin')
run('git', 'ls-remote', '--symref', 'origin', 'HEAD')
print('--- root files on rebuild ---')
run('git', 'ls-tree', '--name-only', 'HEAD')
