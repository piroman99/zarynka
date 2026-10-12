# -*- coding: utf-8 -*-
"""Закадр VN-эп1 ПОСТРАНИЧНО (дословный авторский текст).

Читает vn2/content.js (поле page.vo), синтезирует каждый файл голосом,
зафиксированным Иваном: gemini-3.8-flash-tts, голос Charon, «серьёзная
кинохроника без иронии» (v2). Кладёт в vn2/audio/vo/.

Запуск:  python3 _vn2_vo.py prolog|reception|all
Стоимость: gemini-3.8-flash-tts = 1.70 ₽ / 1000 знаков.
"""
import os, sys, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

OUTDIR = 'vn2/audio/vo'
CAP_RUB = 40.0
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

src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))

group = (sys.argv[1] if len(sys.argv) > 1 else 'all').lower()
if group == 'prolog':
    keep = lambda v: v.startswith('audio/vo/s')
elif group == 'reception':
    keep = lambda v: v.startswith('audio/vo/rec_')
else:
    keep = lambda v: True

items = []
for nd in D['nodes']:
    if nd['t'] != 'scene':
        continue
    for pg in nd['pages']:
        vo = pg.get('vo')
        if vo and keep(vo):
            items.append((vo, pg['tx'].strip()))

chars = sum(len(t) for _, t in items)
print('%s: файлов=%d, знаков=%d, оценка ~%.2f ₽' % (group, len(items), chars, chars * 1.70 / 1000))

os.makedirs(os.path.join(HERE, OUTDIR), exist_ok=True)
spent = 0.0
rep = []
for vo, tx in items:
    name = os.path.basename(vo)[:-4]                 # 's1_00'
    dst = os.path.join(HERE, OUTDIR, name + '.mp3')
    if os.path.exists(dst) and os.path.getsize(dst) > 2000:
        print('  skip %s (есть)' % name)
        rep.append({'file': vo, 'chars': len(tx), 'price': 0, 'skip': True})
        continue
    if spent >= CAP_RUB:
        print('  STOP: cap %.0f ₽' % CAP_RUB); break
    say = re.sub(r'^[\u2014\u2013-]+\s*', '', tx)     # убрать ведущее тире реплики
    say = re.sub(r'\s+', ' ', say)
    try:
        files, st = pv.generate_to_files('gemini-3.8-flash-tts', say, VOICE,
                                         outdir=OUTDIR, name=name, max_price_rub=6)
        got = files[0]
        # gemini отдаёт WAV -> транскодируем в настоящий mp3 (mono 96k)
        tmp = dst + '.tmp.mp3'
        import subprocess
        r = subprocess.run([FF, '-y', '-i', got, '-ar', '44100', '-ac', '1',
                            '-b:a', '96k', tmp], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError('ffmpeg: ' + r.stderr[-200:])
        os.replace(tmp, dst)
        if os.path.abspath(got) != os.path.abspath(dst) and os.path.exists(got):
            os.remove(got)
        price = float(st.get('priceRub') or 0)
        spent += price
        rep.append({'file': vo, 'chars': len(tx), 'price': price})
        print('  OK %-10s %4d зн.  %.2f ₽' % (name, len(tx), price))
    except Exception as e:
        print('  FAIL %s: %s' % (name, e))
        rep.append({'file': vo, 'chars': len(tx), 'price': None, 'err': str(e)})

with open(os.path.join(HERE, OUTDIR, 'report_%s.json' % group), 'w', encoding='utf-8') as f:
    json.dump(rep, f, ensure_ascii=False, indent=2)
print('итого ~%.2f ₽' % spent)
