import os, glob, subprocess, re
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*', 'chrome-linux*', 'chrome'))[0]
IDX = os.path.join(HERE, 'vn2', 'index.html')
for q in ['node=9&page=10', 'node=9&page=32', 'node=9&page=0']:
    url = 'file://' + IDX + '?instant=1&text=1&voice=0&music=0&' + q
    r = subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-gpu',
                        '--virtual-time-budget=4000', '--dump-dom', url],
                       capture_output=True, text=True, timeout=90)
    tags = re.findall(r'<img class="sprite[^>]*>', r.stdout)
    print('Q', q, '->', len(tags), 'sprites')
    for t in tags:
        print('   ', t)
    err = [l for l in r.stderr.splitlines() if 'ERROR' in l or 'Uncaught' in l]
    if err:
        print('   STDERR:', err[:4])
