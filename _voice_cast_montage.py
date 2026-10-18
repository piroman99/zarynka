# -*- coding: utf-8 -*-
"""Склейка тестовых голосов Приёмной в mp3 для прослушки (по персонажу).

Порядок в каждом файле = порядок из отчёта (я перечислю его в сообщении).
Между дублями — 0.7 с тишины, чтобы было слышно, где кончается один голос.
"""
import os, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg',
                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
OUT = os.path.join(HERE, 'assets/audio/vo_cast')
rep = json.load(open(os.path.join(OUT, 'report.json'), encoding='utf-8'))

order = {'starik': [], 'sergey': [], 'kate': []}
for r in rep:
    order[r['key']].append(r)

for key, items in order.items():
    parts = []
    for i, r in enumerate(items):
        src = os.path.join(HERE, r['file'])
        parts.append(src)
        if i != len(items) - 1:
            sil = os.path.join(OUT, '_sil.mp3')
            subprocess.run([FF, '-y', '-f', 'lavfi', '-i',
                            'anullsrc=r=44100:cl=mono', '-t', '0.7',
                            '-b:a', '96k', sil],
                           capture_output=True)
            parts.append(sil)
    lst = os.path.join(OUT, '_list_%s.txt' % key)
    with open(lst, 'w', encoding='utf-8') as f:
        for p in parts:
            f.write("file '%s'\n" % p)
    dst = os.path.join(OUT, 'montage_%s.mp3' % key)
    r = subprocess.run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', lst,
                        '-b:a', '96k', dst], capture_output=True, text=True)
    if r.returncode != 0:
        print('FAIL', key, r.stderr[-300:]); continue
    print('montage_%s.mp3  %.1f KB  порядок: %s' % (
        key, os.path.getsize(dst) / 1024,
        ', '.join(x['voice'] for x in items)))
    os.remove(lst)
os.remove(os.path.join(OUT, '_sil.mp3'))
