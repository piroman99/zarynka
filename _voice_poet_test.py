# -*- coding: utf-8 -*-
"""Тест голоса ПОЭТА (Лёша Савушкин): 6 кандидатов gemini-3.8-flash-tts.

Реплика — его собственная из игры (сцена «аллея у ворот», стр. 12–16 склеены в одну
фразу): «У меня нет научной программы…». Так голос проверяется на том материале,
которым он будет говорить.

Кандидаты подобраны под описание: молодой мужчина ~25, голос мягкий, чуть надломленный,
без театральности, с гордостью за себя и отчаянием. Не бас, не диктор.

Выход: assets/audio/vo_poet/<n>_<voice>.mp3 + склейка с ПРОИЗНЕСЁННЫМИ номерами
montage_poet.mp3 (можно отвечать цифрой). Цена gemini 1.70 ₽ / 1000 зн.

Запуск: python3 _voice_poet_test.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv  # noqa: E402

WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg',
                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
OUT = 'assets/audio/vo_poet'
os.makedirs(os.path.join(HERE, OUT), exist_ok=True)

LINE = ('У меня нет научной программы. Да и откуда она у меня? Я поэт, '
        'я не придумаю программу и за год. А она там ждет меня. '
        'Только я не прилечу к ней.')

STYLE = ('Молодой мужчина двадцати пяти лет, поэт. Голос мягкий, негромкий, '
         'с легкой хрипотцой и надломом. Говорит тихо и сбивчиво, как человек, '
         'который только что плакал: в интонации гордость за себя и отчаяние '
         'одновременно. Без театральности, без пафоса, без жалобы. Не диктор, '
         'не бас, не мальчик-подросток.')

CAND = ['Achird', 'Umbriel', 'Algieba', 'Enceladus', 'Achernar', 'Zubenelgenubi']

LABEL_STYLE = {'gemini_voice': 'Charon', 'engine': 'flash',
               'style_instructions': 'Нейтральный диктор, ровно и чётко.'}

CAP_RUB = 4.0
spent = 0.0
rep = []
seq = []

for i, v in enumerate(CAND, 1):
    if spent >= CAP_RUB:
        print('STOP: cap %.0f ₽' % CAP_RUB)
        break
    name = 'poet_%02d_%s' % (i, v.lower())
    dst = os.path.join(HERE, OUT, name + '.mp3')
    price = 0.0
    if os.path.exists(dst) and os.path.getsize(dst) > 2000:
        print('skip %-2d %-14s (есть)' % (i, v))
    else:
        try:
            files, st = pv.generate_to_files(
                'gemini-3.8-flash-tts', LINE,
                {'gemini_voice': v, 'engine': 'flash', 'style_instructions': STYLE},
                outdir=OUT, name=name, max_price_rub=3)
            got = files[0]
            tmp = dst + '.tmp.mp3'
            r = subprocess.run([FF, '-y', '-i', got, '-ar', '44100', '-ac', '1',
                                '-b:a', '96k', tmp], capture_output=True, text=True)
            if r.returncode != 0:
                raise RuntimeError('ffmpeg: ' + r.stderr[-200:])
            os.replace(tmp, dst)
            os.remove(got)
            price = float(st.get('priceRub') or 0)
            spent += price
            print('ok %-2d %-14s %.2f ₽  %d B' % (i, v, price, os.path.getsize(dst)))
        except Exception as e:  # noqa: BLE001
            print('FAIL %-2d %-14s %s' % (i, v, str(e)[:160]))
            continue
    rep.append({'n': i, 'voice': v, 'file': OUT + '/' + name + '.mp3', 'price': price})
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
        except Exception as e:  # noqa: BLE001
            print('label FAIL %d: %s' % (i, str(e)[:120]))

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
mont = os.path.join(HERE, OUT, 'montage_poet.mp3')
r = subprocess.run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', lst,
                    '-b:a', '96k', mont], capture_output=True, text=True)
print('\nмонтаж:', 'OK' if r.returncode == 0 else r.stderr[-300:])
if r.returncode == 0:
    d = subprocess.run([FF, '-hide_banner', '-i', mont], capture_output=True, text=True)
    import re as _re
    m = _re.search(r'Duration: (\d+):(\d+):([\d.]+)', d.stderr)
    dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0
    print('montage_poet.mp3  %.1f KB  %.1f с' % (os.path.getsize(mont) / 1024, dur))
json.dump(rep, open(os.path.join(HERE, OUT, 'report.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('потрачено ~ %.2f ₽, порядок: %s' % (spent, ', '.join('%d=%s' % (x['n'], x['voice'])
                                                           for x in rep)))
for f in (lst, sil):
    if os.path.exists(f):
        os.remove(f)
