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
    print(r.stdout.strip()[:800])
    if r.stderr.strip():
        print('ERR:', r.stderr.strip()[:400])
    return r

run('git', 'fetch', 'origin', 'master:refs/remotes/origin/master', '--force')
print('--- origin/master top-level (первые 30) ---')
run('git', 'ls-tree', '--name-only', 'origin/master')
print('--- есть ли index.html / vn2 в origin/master ---')
run('git', 'ls-tree', '--name-only', 'origin/master', 'index.html')
run('git', 'ls-tree', '--name-only', 'origin/master', 'vn2/')
print('--- на rebuild ---')
run('git', 'ls-tree', '--name-only', 'HEAD', 'index.html')
run('git', 'ls-tree', '--name-only', 'HEAD', 'vn2/')
run('git', 'ls-tree', '--name-only', 'HEAD', '.nojekyll')
print('--- счётчики коммитов ---')
run('git', 'rev-list', '--count', 'origin/master')
run('git', 'rev-list', '--count', 'HEAD')
