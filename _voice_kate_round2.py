# -*- coding: utf-8 -*-
"""Голос Екатерины, раунд 2: непроверенные женские голоса ElevenLabs
(Rachel/Aria/Laura/Alice/Jessica/Lily) + старые три (Sarah/Matilda/Charlotte)
в одном монтаже с произнесёнными номерами.

Реплика — та же, что в первом тесте (`_vn2_kate_test.py`), чтобы сравнивать
один в один. ElevenLabs 10.84 ₽/1000 зн. → ~1.35 ₽ за голос.
"""
import os, sys, subprocess, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg',
                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
OUT = 'assets/audio/vo_kate2'
os.makedirs(os.path.join(HERE, OUT), exist_ok=True)

LINE = ("Вы хотите сказать, что я слишком старая, чтобы лететь в космос? "
        "Но на орбитальную станцию летали люди старше меня.")

NEW = ['Rachel', 'Aria', 'Laura', 'Alice', 'Jessica', 'Lily']
OLD = ['Sarah', 'Matilda', 'Charlotte']

LABEL_STYLE = {"gemini_voice": "Charon", "engine": "flash",
               "style_instructions": "Нейтральный диктор, ровно и чётко."}

rep = []
seq = []
for i, v in enumerate(NEW + OLD, 1):
    name = 'kate2_%02d_%s' % (i, v.lower())
    dst = os.path.join(HERE, OUT, name + '.mp3')
    if not (os.path.exists(dst) and os.path.getsize(dst) > 2000):
        try:
            files, st = pv.generate_to_files('elevenlabs-v4-tts', LINE,
                                             {'voice': v}, outdir=OUT,
                                             name=name, max_price_rub=6)
            got = files[0]
            tmp = dst + '.tmp.mp3'
            r = subprocess.run([FF, '-y', '-i', got, '-ar', '44100', '-ac', '1',
                                '-b:a', '96k', tmp], capture_output=True, text=True)
            if r.returncode != 0:
                raise RuntimeError('ffmpeg: ' + r.stderr[-200:])
            os.replace(tmp, dst)
            os.remove(got)
            price = float(st.get('priceRub') or 0)
            print('ok %-2d %-10s %.2f ₽' % (i, v, price))
        except Exception as e:
            print('FAIL %-2d %-10s %s' % (i, v, e))
            continue
    else:
        print('skip %-2d %-10s (есть)' % (i, v))
        price = 0.0
    rep.append({'n': i, 'voice': v, 'file': OUT + '/' + name + '.mp3',
                'price': price})
    seq.append((i, v, dst))

# произнесённые номера
for i, v, dst in seq:
    lp = os.path.join(HERE, OUT, 'lbl_%02d.mp3' % i)
    if not (os.path.exists(lp) and os.path.getsize(lp) > 1500):
        try:
            files, st = pv.generate_to_files('gemini-3.8-flash-tts',
                                             'Вариант %d.' % i, LABEL_STYLE,
                                             outdir=OUT, name='lbl_%02d' % i,
                                             max_price_rub=2)
            got = files[0]
            r = subprocess.run([FF, '-y', '-i', got, '-ar', '44100', '-ac', '1',
                                '-b:a', '96k', lp], capture_output=True, text=True)
            if r.returncode != 0:
                raise RuntimeError(r.stderr[-200:])
            os.remove(got)
        except Exception as e:
            print('label FAIL %d: %s' % (i, e)); continue
    seq_ok = True

# склейка: номер -> реплика -> 0.6 с тишины
sil = os.path.join(HERE, OUT, '_sil.mp3')
subprocess.run([FF, '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-t', '0.6', '-b:a', '96k', sil], capture_output=True)
parts = []
for i, v, dst in seq:
    lp = os.path.join(HERE, OUT, 'lbl_%02d.mp3' % i)
    if os.path.exists(lp):
        parts.append(lp)
    parts.append(dst)
    parts.append(sil)
lst = os.path.join(HERE, OUT, '_list.txt')
with open(lst, 'w', encoding='utf-8') as f:
    for p in parts:
        f.write("file '%s'\n" % p)
mont = os.path.join(HERE, OUT, 'montage_kate2.mp3')
r = subprocess.run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', lst,
                    '-b:a', '96k', mont], capture_output=True, text=True)
print('montage:', 'OK' if r.returncode == 0 else r.stderr[-300:])
os.remove(lst); os.remove(sil)
json.dump(rep, open(os.path.join(HERE, OUT, 'report.json'), 'w'),
          ensure_ascii=False, indent=2)
print('итого %.2f ₽' % sum(r['price'] for r in rep))
print('порядок:', ', '.join('%d=%s' % (r['n'], r['voice']) for r in rep))
