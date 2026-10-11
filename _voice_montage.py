# -*- coding: utf-8 -*-
"""Склейка тестовых голосов в один mp3 (по порядку, с паузами).
Выход: assets/audio/vo_test/montage_voices.mp3
"""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg',
                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
FF = os.path.abspath(FF)
D = os.path.join(HERE, 'assets', 'audio', 'vo_test')
ORDER = [
    ('gpt_onyx_0.mp3',        '1) gpt-4o-mini-tts — onyx'),
    ('gemini_charon_0.wav',   '2) gemini-3.8-flash-tts — Charon'),
    ('qwen_unclefu_0.mp3',    '3) qwen3-tts — Uncle_Fu'),
    ('elv_roger_0.mp3',       '4) elevenlabs-v4 — Roger'),
]
TMP = os.path.join(HERE, '.tmp_vo')
os.makedirs(TMP, exist_ok=True)

parts = []
for i, (fn, label) in enumerate(ORDER):
    src = os.path.join(D, fn)
    dst = os.path.join(TMP, 'p%d.wav' % i)
    r = subprocess.run([FF, '-y', '-i', src, '-ar', '44100', '-ac', '1',
                        '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', dst],
                       capture_output=True, text=True)
    print('conv', fn, 'rc', r.returncode)
    parts.append(dst)
    sil = os.path.join(TMP, 's%d.wav' % i)
    subprocess.run([FF, '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                    '-t', '0.9', sil], capture_output=True, text=True)
    parts.append(sil)

lst = os.path.join(TMP, 'list.txt')
with open(lst, 'w') as f:
    for p in parts:
        f.write("file '%s'\n" % p.replace("'", "'\\''"))
out = os.path.join(D, 'montage_voices.mp3')
r = subprocess.run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', lst,
                    '-c:a', 'libmp3lame', '-b:a', '192k', out],
                   capture_output=True, text=True)
print('montage rc', r.returncode, os.path.relpath(out, HERE),
      os.path.getsize(out) if os.path.exists(out) else 0)
if r.returncode:
    print(r.stderr[-800:])
print('\nпорядок:')
for fn, label in ORDER:
    print('  ', label)
