# -*- coding: utf-8 -*-
"""Закадр для ПЕРВОЙ страницы кадра s1 (новый кадр «Звёздный городок, стена, граффити»).

2026-11-04 (решение Ивана, развилка A): абзац L[5] разделён на две страницы —
  стр. 1 «Кто бросил клич… работников Звездного городка.» → новый кадр s1a (стена),
  стр. 2 «Очень уж хотелось поймать этого умника в темной подворотне…» → старый s1.
Оба текста изменились, поэтому оба mp3 переписываются заново (s1_00 был целым абзацем).

Читает vn2/content.js (значит, запускать ПОСЛЕ сборки), синтезирует по одной mp3
голосом закадра (gemini-3.8-flash-tts, Charon — тот же голос, что и весь пролог).
gemini отдаёт WAV -> транскодируем в mono 96k mp3 (ffmpeg из .probe).

Запуск: python3 _prolog_vo_s1.py [--dry] [--force=s1_00,s1_01]
Стоимость: 1.70 ₽ / 1000 знаков (~0.6 ₽ на две страницы).
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
FRAMES = ('s1',)
DRY = '--dry' in sys.argv
FORCE = set()
for a in sys.argv[1:]:
    if a.startswith('--force='):
        FORCE = {x.strip() for x in a.split('=', 1)[1].split(',') if x.strip()}
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

items = []
for nd in D['nodes']:
    if nd['t'] != 'scene' or nd.get('id') not in FRAMES:
        continue
    for pg in nd['pages']:
        if pg.get('vo'):
            items.append((nd['id'], pg['vo'], pg['tx'].strip()))
        if pg.get('bg'):
            print('  страница со своим кадром: %s' % pg['bg'])

chars = sum(len(t) for _, _, t in items)
print('кадр %s: файлов=%d, знаков=%d, оценка ~%.2f ₽'
      % ('/'.join(FRAMES), len(items), chars, chars * 1.70 / 1000))
for fr, vo, tx in items:
    print('  %-6s %-22s %3d зн.  %s' % (fr, os.path.basename(vo), len(tx), tx[:80]))
if DRY:
    raise SystemExit(0)

spent = 0.0
for fr, vo, tx in items:
    name = os.path.basename(vo)[:-4]
    dst = os.path.join(OUTDIR, name + '.mp3')
    if os.path.exists(dst) and os.path.getsize(dst) > 2000 and name not in FORCE:
        print('  skip %-20s (есть)' % name)
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

have = {os.path.basename(vo)[:-4] for _, vo, _ in items}
for p in sorted(os.listdir(OUTDIR)):
    if p.startswith('s1_') and p.endswith('.mp3') and p[:-4] not in have:
        os.remove(os.path.join(OUTDIR, p))
        print('  удалён устаревший', p)

print('итого ~%.2f ₽' % spent)
