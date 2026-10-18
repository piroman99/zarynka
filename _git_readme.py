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
    print(r.stdout.strip()[:700])
    if r.stderr.strip():
        print('ERR:', r.stderr.strip()[:400])
    return r

run('git', 'add', 'README.md', '_git_state.py', '_git_state2.py', '_git_merge.py',
    '_git_pages_check.py')
run('git', 'commit', '-m',
    'README: branch layout (master mirrors rebuild, old = 2016 archive) and demo link')
run('git', 'push', 'origin', 'HEAD:rebuild')
run('git', 'push', 'origin', 'rebuild:master', '--force')
run('git', 'ls-remote', '--heads', 'origin')
