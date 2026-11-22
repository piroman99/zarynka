import hashlib, os, subprocess, sys

FIN = 'assets/final/prolog'
def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

before = {f: md5(os.path.join(FIN, f)) for f in sorted(os.listdir(FIN)) if f.endswith('.png')}
print('before:', len(before))
r = subprocess.run(['/usr/bin/python3', '_prolog_finals.py', 's7'], capture_output=True, text=True)
print(r.stdout[-2000:])
print(r.stderr[-2000:])
after = {f: md5(os.path.join(FIN, f)) for f in sorted(os.listdir(FIN)) if f.endswith('.png')}
changed = [f for f in after if before.get(f) != after[f]]
print('changed:', changed)
print('s7 size', os.path.getsize(os.path.join(FIN, 's7.png')))
