import os, subprocess

WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEY = os.path.join(WS, '.ssh', 'github_ed25519')
KNOWN = os.path.join(WS, '.ssh', 'known_hosts')
env = dict(os.environ)
env['GIT_SSH_COMMAND'] = ('ssh -i %s -o IdentitiesOnly=yes -o UserKnownHostsFile=%s '
                          '-o StrictHostKeyChecking=no' % (KEY, KNOWN))

def run(*a):
    r = subprocess.run(list(a), capture_output=True, text=True, env=env)
    print('$', ' '.join(a), '-> rc', r.returncode, r.stdout.strip()[:300], r.stderr.strip()[:300])
    return r

run('git', 'add', 'STATUS.md', '_git_readme.py')
run('git', 'commit', '-m', 'docs: record the new branch layout (master mirror, old archive)')
run('git', 'push', 'origin', 'HEAD:rebuild')
run('git', 'push', 'origin', 'rebuild:master', '--force')
run('git', 'ls-remote', '--heads', 'origin')
run('git', 'log', '--oneline', '-3')
