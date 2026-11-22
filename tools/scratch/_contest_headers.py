#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
def run(args):
    p = subprocess.run(args, capture_output=True)
    return p.returncode, p.stdout.decode('utf-8','replace'), p.stderr.decode('utf-8','replace')[:300]

U = 'https://2061.su/media/cache/77/a3/77a3150b1a9b88b6c93ffa03754be76a.jpg'
print('--- headers 2061.su ---')
print(run(['curl','-skIL','-m','40','-A','Mozilla/5.0',U])[1][:800])
print('--- headers wayback ---')
W = 'https://web.archive.org/web/20160510014641id_/https://2061.su/konkursy/zaryanka-illustrations/iwork/baba-katia/'
print(run(['curl','-skIL','-m','40','-A','Mozilla/5.0',W])[1][:800])
