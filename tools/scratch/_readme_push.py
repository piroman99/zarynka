import os, subprocess, urllib.request, time, hashlib

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

run('git', 'add', 'README.md')
run('git', 'commit', '-m', 'README: rewrite for the current state of the pilot (ep-1, vn2, build steps)')
run('git', 'push', 'origin', 'HEAD:rebuild')
run('git', 'push', 'origin', 'rebuild:master', '--force')
run('git', 'log', '--oneline', '-1')

# проверка, что GitHub отдал новый README
url = 'https://raw.githubusercontent.com/piroman99/zarynka/master/README.md'
local = open('README.md', 'rb').read()
for i in range(6):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'check/1.0', 'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=40) as r:
            data = r.read()
        print('raw README %d B  %s' % (len(data), 'MATCH' if hashlib.md5(data).hexdigest() == hashlib.md5(local).hexdigest() else 'old'))
        if data == local:
            break
    except Exception as e:
        print('!!', repr(e)[:100])
    time.sleep(15)
