import hashlib, os, subprocess

LOCAL = 'vn2/img/prolog/s7.webp'
md5 = hashlib.md5(open(LOCAL, 'rb').read()).hexdigest()
print('local s7.webp', os.path.getsize(LOCAL), md5)
print('final s7.png', os.path.getsize('assets/final/prolog/s7.png'))

# все кадры в сборке на месте?
for n in ('s1', 's2', 's3', 's4', 's5', 's6', 's7'):
    p = 'vn2/img/prolog/%s.webp' % n
    print('  %s %8d B  %s' % (n, os.path.getsize(p), 'OK' if os.path.exists(p) else 'НЕТ'))

WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEY = os.path.join(WS, '.ssh', 'github_ed25519')
KNOWN = os.path.join(WS, '.ssh', 'known_hosts')
env = dict(os.environ)
env['GIT_SSH_COMMAND'] = ('ssh -i %s -o IdentitiesOnly=yes -o UserKnownHostsFile=%s '
                          '-o StrictHostKeyChecking=no' % (KEY, KNOWN))
subprocess.run(['git', 'add', 'PROLOG_FIXES.md', 'STATUS.md'], capture_output=True, text=True)
r = subprocess.run(['git', 'commit', '-m', 'S7: closed - Ivan accepted the quiet plaque (variant A)'],
                   capture_output=True, text=True)
print(r.stdout[-300:])
r = subprocess.run(['git', 'push', 'origin', 'HEAD:rebuild'], capture_output=True, text=True, env=env)
print('push rc', r.returncode, r.stdout[-200:], r.stderr[-200:])
print(subprocess.run(['git', 'log', '--oneline', '-2'], capture_output=True, text=True).stdout)
