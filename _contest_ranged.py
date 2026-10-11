#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Скачивание больших файлов чанками через Range (обход обрыва ~16КБ)."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '.tmp2061', 'refetch')
os.makedirs(OUT, exist_ok=True)

U = sys.argv[1] if len(sys.argv) > 1 else \
    'https://2061.su/media/cache/77/a3/77a3150b1a9b88b6c93ffa03754be76a.jpg'
DEST = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT, 'chunk_test.jpg')
CHUNK = 8192

def curl(args):
    return subprocess.run(args, capture_output=True)

def clen(url):
    p = curl(['curl', '-skIL', '-m', '40', '-A', 'Mozilla/5.0', url])
    for line in p.stdout.decode('utf-8', 'replace').splitlines():
        if line.lower().startswith('content-length:'):
            return int(line.split(':')[1].strip())
    return None

total = clen(U)
print('content-length:', total)
if not total:
    print('нет длины — пробуем обычную загрузку'); sys.exit(1)

buf = bytearray()
start = 0
while start < total:
    end = min(start + CHUNK - 1, total - 1)
    cmd = ['curl', '-sk', '-m', '60', '-A', 'Mozilla/5.0',
           '-H', f'Range: bytes={start}-{end}', U]
    p = subprocess.run(cmd, capture_output=True)
    got = p.stdout
    if not got:
        print(f'  обрыв на {start} (rc={p.returncode})'); break
    buf += got
    start += len(got)
    if len(got) < (end - start + len(got) + 1):
        pass
print('собрано', len(buf), 'из', total)
open(DEST, 'wb').write(buf)
ok = bytes(buf).endswith(b'\xff\xd9')
print('saved', DEST, 'EOI=', ok)
