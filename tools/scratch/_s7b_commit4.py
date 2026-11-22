import os, subprocess

WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEY = os.path.join(WS, '.ssh', 'github_ed25519')
KNOWN = os.path.join(WS, '.ssh', 'known_hosts')
env = dict(os.environ)
env['GIT_SSH_COMMAND'] = ('ssh -i %s -o IdentitiesOnly=yes -o UserKnownHostsFile=%s '
                          '-o StrictHostKeyChecking=no' % (KEY, KNOWN))

FILES = ['PROLOG_FIXES.md', 'STATUS.md', '_prolog_finals.py', '_s7_plaque2.py',
         '_s7_plaque.py', '_s7b_quiet.py', '_s7b_quiet2.py', '_s7b_quiet3.py',
         '_s7b_zoom.py', 'assets/final/prolog/s7.png', 'vn2/img/prolog/s7.webp',
         'assets/review/review_131_s7_plaque_quiet.png',
         'assets/review/review_131b_s7_quiet_full.jpg',
         'assets/review/review_132_s7_plaque_quiet_vn.png',
         'assets/review/review_133_s7_plaque_zoom.png',
         'assets/review/review_96_s7_vn_ok.png']
print(subprocess.run(['git', 'add'] + FILES, capture_output=True, text=True).stdout)
print(subprocess.run(['git', 'status', '--short'] + FILES, capture_output=True, text=True).stdout)
msg = """S7: make the wall plaque quiet

Ivan: "too noticeable". New style A: 96x56 (was 128x76), plate tone matched to
the wall (162,146,136), dark engraved lettering instead of red enamel, softer
shadow, thin edge. Letters stay legible only up close; at frame scale it is a
faint mark on the wall. Styles B (single line, tiny) and C (old size, no red)
left in _s7_plaque2.py for reference; comparison sheet review_131.
"""
r = subprocess.run(['git', 'commit', '-m', msg], capture_output=True, text=True)
print(r.stdout[-900:], r.stderr[-400:])
r = subprocess.run(['git', 'push', 'origin', 'HEAD:rebuild'], capture_output=True, text=True, env=env)
print('push rc', r.returncode, r.stdout[-300:], r.stderr[-300:])
