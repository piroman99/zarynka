# -*- coding: utf-8 -*-
"""Закадр для кадров 9-12 (2026-11-01): новые узлы s5a (площадь) и s5b (Верховный Совет).

Третий кусок SEG9 разрезан по фразе «Волна требований докатилась…» на два кадра:
  s5a — «Через неделю лозунг…» + «Вопрос, к великому удивлению…» (2 страницы)
  s5b — «Волна требований докатилась до Верховного Совета…» (1 страница)
Старые s5_00/s5_01 относятся к прежнему узлу s5 и больше не используются.

Голос тот же, что у всего пролога: gemini-3.8-flash-tts, Charon, «серьёзная
кинохроника без иронии». Готовые файлы пропускаются, на media_generation_failed —
ретрай (готча PlusVibe TTS: одиночная страница иногда падает, лечится перезапуском).

Запуск: python3 _prolog_vo_s5ab.py [--dry] [--force имя_файла ...]
Стоимость: 1.70 ₽ / 1000 знаков.
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
MAN = os.path.join(OUTDIR, '_voices.json')
FRAMES = ('s5a', 's5b')
DRY = '--dry' in sys.argv
FORCE = set(a for a in sys.argv[1:] if not a.startswith('--'))
TRIES = 4
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg',
                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2')

VOICE = {
    "gemini_voice": "Charon", "engine": "flash",
    "style_instructions": (
        "Спокойный, зрелый мужской закадровый голос. Документальная кинохроника: "
        "серьёзно, сдержанно, ровно, без иронии, без насмешки и без пафоса. "
        "Говори не спеша, чуть медленнее обычного, с небольшими паузами между фразами. "
        "Нейтральная чёткая дикция, доверительная интонация рассказчика."
    ),
}


def to_mp3(src, dst):
    """WAV от gemini -> настоящий mp3 (mono 96k)."""
    tmp = dst + '.tmp.mp3'
    r = subprocess.run([FF, '-y', '-i', src, '-ar', '44100', '-ac', '1',
                        '-b:a', '96k', tmp], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError('ffmpeg: ' + r.stderr[-200:])
    os.replace(tmp, dst)
    if os.path.abspath(src) != os.path.abspath(dst) and os.path.exists(src):
        os.remove(src)


src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))
man = json.load(open(MAN, encoding='utf-8')) if os.path.exists(MAN) else {}

items = []
for nd in D['nodes']:
    if nd['t'] != 'scene' or nd.get('id') not in FRAMES:
        continue
    for pg in nd['pages']:
        vo = pg.get('vo')
        if vo:
            items.append((nd['id'], vo, pg['tx'].strip()))

chars = sum(len(t) for _, _, t in items)
print('кадры %s: файлов=%d, знаков=%d, оценка ~%.2f ₽'
      % ('/'.join(FRAMES), len(items), chars, chars * 1.70 / 1000))
for fr, vo, tx in items:
    done = os.path.exists(os.path.join(OUTDIR, os.path.basename(vo)[:-4] + '.mp3'))
    same = (man.get(vo, {}).get('text') == tx)
    state = 'есть/текст совпал' if (done and same) else ('ПЕРЕозвучить' if done else 'новый')
    print('  %-6s %-22s %3d зн.  %-18s %s' % (fr, os.path.basename(vo), len(tx), state, tx[:60]))
if DRY:
    raise SystemExit(0)

spent = 0.0
for fr, vo, tx in items:
    name = os.path.basename(vo)[:-4]
    dst = os.path.join(OUTDIR, name + '.mp3')
    fresh = (os.path.exists(dst) and os.path.getsize(dst) > 2000
             and man.get(vo, {}).get('text') == tx and name not in FORCE)
    if fresh:
        print('  skip %-20s (есть, текст совпал)' % name)
        continue
    stray = os.path.join(OUTDIR, name + '_0.wav')
    if os.path.exists(stray) and os.path.getsize(stray) > 20000:
        to_mp3(stray, dst)
        print('  OK   %-20s (из готового wav)' % name)
        continue
    say = re.sub(r'^[\u2014\u2013-]+\s*', '', tx)
    say = re.sub(r'\s+', ' ', say)
    for attempt in range(1, TRIES + 1):
        try:
            files, st = pv.generate_to_files('gemini-3.8-flash-tts', say, VOICE,
                                             outdir=os.path.join('vn2', 'audio', 'vo'),
                                             name=name, max_price_rub=6)
            to_mp3(files[0], dst)
            price = float(st.get('priceRub') or 0)
            spent += price
            print('  OK   %-20s %4d зн.  %.2f ₽' % (name, len(tx), price))
            break
        except Exception as e:
            print('  %s %-20s попытка %d: %s'
                  % ('FAIL' if attempt == TRIES else 'retry', name, attempt, str(e)[:120]))

print('итого ~%.2f ₽' % spent)
