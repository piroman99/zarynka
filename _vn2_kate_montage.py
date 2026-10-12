# -*- coding: utf-8 -*-
"""Монтаж голосового теста Екатерины: «Вариант N» + реплика, по кругу."""
import os, subprocess, glob
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
D = os.path.join(HERE, 'assets', 'audio', 'vo_kate')
TMP = os.path.join(D, '_wav')
os.makedirs(TMP, exist_ok=True)


def run(args):
    return subprocess.run([FF, '-y'] + args, capture_output=True, text=True)


def to_wav(src, dst):
    run(['-i', src, '-ar', '44100', '-ac', '1', dst])


# тишина 0.5 с
run(['-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', '0.5', os.path.join(TMP, 'sil.wav')])

parts = []
for i in range(1, 8):
    n = '%02d' % i
    for tag, src in (('lbl', 'lbl_%s_0.wav' % n), ('kate', None)):
        if tag == 'lbl':
            s = os.path.join(D, src)
        else:
            cand = glob.glob(os.path.join(D, 'kate_%s_0.*' % n))[0]
            s = cand
        w = os.path.join(TMP, '%s_%s.wav' % (tag, n))
        to_wav(s, w)
        parts.append(w)

# порядок: sil lbl kate sil lbl kate ...
order = []
for i in range(1, 8):
    n = '%02d' % i
    order += [os.path.join(TMP, 'sil.wav'), os.path.join(TMP, 'lbl_%s.wav' % n),
              os.path.join(TMP, 'kate_%s.wav' % n)]
order.append(os.path.join(TMP, 'sil.wav'))

lst = os.path.join(TMP, 'list.txt')
with open(lst, 'w') as f:
    for p in order:
        f.write("file '%s'\n" % p)

out = os.path.join(D, 'montage_kate.mp3')
r = run(['-f', 'concat', '-safe', '0', '-i', lst, '-ar', '44100', '-ac', '1',
         '-b:a', '128k', out])
print('rc', r.returncode, r.stderr[-300:] if r.returncode else '')
print('OUT', out, os.path.getsize(out) if os.path.exists(out) else 'нет')
