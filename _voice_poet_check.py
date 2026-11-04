# -*- coding: utf-8 -*-
"""Проверка теста голосов поэта: файлы РАЗНЫЕ (не сработал fallback), длины вменяемые.

Готча прошлых раундов: если имя голоса модель не знает, она молча отдаёт голос по
умолчанию — тогда 6 «кандидатов» звучат одинаково. Ловим по md5 и по длительности.
"""
import hashlib
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg',
                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
OUT = os.path.join(HERE, 'assets', 'audio', 'vo_poet')


def dur(p):
    r = subprocess.run([FF, '-hide_banner', '-i', p], capture_output=True, text=True)
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', r.stderr)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0.0


files = sorted(f for f in os.listdir(OUT) if f.startswith('poet_') and f.endswith('.mp3'))
hashes = {}
ok = True
for f in files:
    p = os.path.join(OUT, f)
    h = hashlib.md5(open(p, 'rb').read()).hexdigest()
    d = dur(p)
    dup = hashes.get(h)
    hashes.setdefault(h, f)
    flag = 'ДУБЛЬ с ' + dup if dup else 'уникален'
    good = (not dup) and 8.0 < d < 40.0
    ok = ok and good
    print('%s %-30s %5.1f с  %7d B  %s' % ('OK  ' if good else 'FAIL', f, d,
                                           os.path.getsize(p), flag))

print('\nфайлов %d, уникальных %d' % (len(files), len(hashes)))
mont = os.path.join(OUT, 'montage_poet.mp3')
if os.path.exists(mont):
    print('монтаж %.1f с, %d KB' % (dur(mont), os.path.getsize(mont) / 1024))
print('ИТОГ:', 'все голоса разные' if ok else 'ЕСТЬ ПРОБЛЕМЫ')
