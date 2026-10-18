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
    print(r.stdout.strip()[:900])
    if r.stderr.strip():
        print('ERR:', r.stderr.strip()[:600])
    return r

# 1) архив 2016 сохраняем в ветку old
run('git', 'branch', '-f', 'old', 'origin/master')
run('git', 'push', 'origin', 'old:old')
# 2) master становится зеркалом rebuild (история 2016 остаётся в old)
run('git', 'push', 'origin', 'rebuild:master', '--force')
# 3) проверяем
run('git', 'ls-remote', '--heads', 'origin')
run('git', 'ls-remote', '--symref', 'origin', 'HEAD')
