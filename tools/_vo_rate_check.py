#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Длительность каждого vo-файла против длины текста страницы.
Скорость речи у Charon ~13-16 знаков/с. Резкое расхождение = в файле другой текст."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
VN2 = os.path.join(ROOT, 'vn2')
VO = os.path.join(VN2, 'audio', 'vo')
WS = os.path.abspath(os.path.join(ROOT, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries',
                  'ffmpeg-linux-x86_64-v7.0.2')


def dur(path):
    out = subprocess.run([FF, '-hide_banner', '-i', path], capture_output=True, text=True).stderr
    for line in out.splitlines():
        if 'Duration:' in line:
            h, m, s = line.split('Duration:')[1].split(',')[0].strip().split(':')
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 0.0


src = open(os.path.join(VN2, 'content.js'), encoding='utf-8').read()
content = json.loads(src[src.index('{'):src.rindex('}') + 1])

import _vo_util as U
segs = U.segments(content)
man = json.load(open(os.path.join(VO, '_voices.json'), encoding='utf-8'))

rows = []
for nid, k, vo, tx, who in segs:
    p = os.path.join(VN2, vo)
    d = dur(p)
    n_ch = len(tx)
    rate = n_ch / d if d else 0
    rows.append((nid, k, vo, d, n_ch, rate, tx[:50]))

print('%-12s %3s %-22s %7s %5s %6s' % ('узел', '#', 'файл', 'сек', 'зн', 'зн/с'))
bad = []
for nid, k, vo, d, n_ch, rate, tx in rows:
    flag = ''
    if d and (rate < 8 or rate > 24):
        flag = '  <<< подозрительно'
        bad.append((nid, k, vo, d, n_ch, rate, tx))
    print('%-12s %3d %-22s %7.2f %5d %6.1f%s' % (nid, k, os.path.basename(vo), d, n_ch, rate, flag))
tot = sum(r[3] for r in rows)
print('\nвсего озвучки: %.1f с (%d файлов), подозрительных: %d' % (tot, len(rows), len(bad)))
