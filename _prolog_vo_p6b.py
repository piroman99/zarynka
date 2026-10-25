# -*- coding: utf-8 -*-
"""Добить закадр p6_01 и переписать s2_00 (старый файл от длинной страницы).

Готча PlusVibe TTS: часть страниц стабильно падает с media_generation_failed
(лечится перезапуском, но иногда — нет). Тогда режем страницу на предложения,
синтезируем по частям и склеиваем ffmpeg'ом (concat), сохраняя имя файла.

Запуск: python3 _prolog_vo_p6b.py [--dry]
"""
import os
import re
import sys
import json
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

OUTDIR = os.path.join(HERE, 'vn2', 'audio', 'vo')
FORCE = {'s2_00'}            # переписать принудительно (текст страницы изменился)
TRIES = 3
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg',
                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
DRY = '--dry' in sys.argv

VOICE = {
    "gemini_voice": "Charon", "engine": "flash",
    "style_instructions": (
        "Спокойный, зрелый мужской закадровый голос. Документальная кинохроника: "
        "серьёзно, сдержанно, ровно, без иронии, без насмешки и без пафоса. "
        "Говори не спеша, чуть медленнее обычного, с небольшими паузами между фразами. "
        "Нейтральная чёткая дикция, доверительная интонация рассказчика."
    ),
}
SENT = re.compile(r'(?<=[.!?…])\s+(?=[А-ЯЁ«])')


def to_mp3(src, dst):
    tmp = dst + '.tmp.mp3'
    r = subprocess.run([FF, '-y', '-i', src, '-ar', '44100', '-ac', '1',
                        '-b:a', '96k', tmp], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError('ffmpeg: ' + r.stderr[-200:])
    os.replace(tmp, dst)
    if os.path.abspath(src) != os.path.abspath(dst) and os.path.exists(src):
        os.remove(src)


def synth(name, text, tag=''):
    say = re.sub(r'\s+', ' ', text.strip())
    files, st = pv.generate_to_files('gemini-3.8-flash-tts', say, VOICE,
                                     outdir=os.path.join('vn2', 'audio', 'vo'),
                                     name=name + tag, max_price_rub=6)
    return files[0], float(st.get('priceRub') or 0)


def concat(parts, dst):
    lst = dst + '.txt'
    with open(lst, 'w', encoding='utf-8') as f:
        for p in parts:
            f.write("file '%s'\n" % os.path.abspath(p).replace("'", "'\\''"))
    tmp = dst + '.tmp.mp3'
    r = subprocess.run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', lst,
                        '-ar', '44100', '-ac', '1', '-b:a', '96k', tmp],
                       capture_output=True, text=True)
    os.remove(lst)
    if r.returncode != 0:
        raise RuntimeError('ffmpeg concat: ' + r.stderr[-200:])
    os.replace(tmp, dst)
    for p in parts:
        if os.path.exists(p):
            os.remove(p)


src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))

want = {}
for nd in D['nodes']:
    if nd['t'] != 'scene' or nd.get('id') not in ('p6', 's2'):
        continue
    for pg in nd['pages']:
        vo = pg.get('vo')
        if vo:
            want[os.path.basename(vo)[:-4]] = pg['tx'].strip()

targets = ['p6_01', 's2_00']
print('цели:', [t for t in targets if t in want])
if DRY:
    for t in targets:
        print(' ', t, want.get(t, '<нет страницы>')[:90])
    raise SystemExit(0)

spent = 0.0
for name in targets:
    tx = want.get(name)
    if not tx:
        print('  нет страницы', name)
        continue
    dst = os.path.join(OUTDIR, name + '.mp3')
    if name in FORCE and os.path.exists(dst):
        os.remove(dst)
        print('  старый %s.mp3 удалён (текст изменился)' % name)
    if os.path.exists(dst) and os.path.getsize(dst) > 2000:
        print('  skip', name)
        continue
    ok = False
    for attempt in range(1, TRIES + 1):
        try:
            f, price = synth(name, tx)
            to_mp3(f, dst)
            spent += price
            print('  OK   %-8s целиком  %.2f ₽' % (name, price))
            ok = True
            break
        except Exception as e:
            print('  retry %-8s попытка %d: %s' % (name, attempt, str(e)[:110]))
    if ok:
        continue
    # не вышло целиком — по предложениям и склейка
    sents = [s.strip() for s in SENT.split(tx) if s.strip()]
    print('  дроблю %s на %d части' % (name, len(sents)))
    parts, failed = [], False
    for i, s in enumerate(sents):
        try:
            f, price = synth(name, s, tag='_p%d' % i)
            spent += price
            parts.append(f)
            print('    часть %d OK (%.2f ₽): %s' % (i, price, s[:50]))
        except Exception as e:
            print('    часть %d FAIL: %s' % (i, str(e)[:110]))
            failed = True
            break
    if not failed and len(parts) > 1:
        concat(parts, dst)
        print('  OK   %-8s склейка %d частей' % (name, len(parts)))

print('итого ~%.2f ₽' % spent)
