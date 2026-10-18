# -*- coding: utf-8 -*-
"""Озвучка Приёмной ГОЛОСАМИ КАСТА (постранично, по полю page.who).

Голоса зафиксированы Иваном (2026-10-18):
  закадр/автор  -> gemini-3.8-flash-tts  Charon  «кинохроника без иронии»
  Старик        -> gemini-3.8-flash-tts  Fenrir
  Сергей        -> gemini-3.8-flash-tts  Charon
  Екатерина     -> elevenlabs-v4-tts     Charlotte   (вариант 9)

Манифест vn2/audio/vo/_voices.json хранит, каким голосом сделан каждый файл:
повторный запуск переозвучивает ТОЛЬКО страницы, чей голос изменился.

  python3 _vn2_vo_cast.py --dry     # только смета
  python3 _vn2_vo_cast.py           # записать
"""
import os, sys, json, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg',
                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
OUTDIR = os.path.join(HERE, 'vn2', 'audio', 'vo')
MANIFEST = os.path.join(OUTDIR, '_voices.json')
CAP_RUB = 30.0
DRY = '--dry' in sys.argv

NARR_STYLE = (
    "Спокойный, зрелый мужской закадровый голос. Документальная кинохроника: "
    "серьёзно, сдержанно, ровно, без иронии, без насмешки и без пафоса. "
    "Говори не спеша, чуть медленнее обычного, с небольшими паузами между фразами. "
    "Нейтральная чёткая дикция, доверительная интонация рассказчика."
)
STARIK_STYLE = (
    "Очень немолодой мужчина, начальник. Голос сухой, низкий, устало-"
    "начальственный. Говорит негромко, но веско, с раздражением, которое он "
    "не повышает. Без театральности и без пафоса."
)
SERGEY_STYLE = (
    "Мужчина около шестидесяти, инженер, много лет на службе. Голос спокойный, "
    "ровный, вежливо-официальный, немного усталый. Чёткая дикция, доброжелательно, "
    "но сдержанно, без иронии."
)

VOICES = {
    'narr':     ('gemini-3.8-flash-tts', {'gemini_voice': 'Charon', 'engine': 'flash',
                                          'style_instructions': NARR_STYLE}, 1.70),
    'Старик':   ('gemini-3.8-flash-tts', {'gemini_voice': 'Fenrir', 'engine': 'flash',
                                          'style_instructions': STARIK_STYLE}, 1.70),
    'Сергей':   ('gemini-3.8-flash-tts', {'gemini_voice': 'Charon', 'engine': 'flash',
                                          'style_instructions': SERGEY_STYLE}, 1.70),
    'Екатерина': ('elevenlabs-v4-tts', {'voice': 'Charlotte'}, 10.84),
}

src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))
nd = [n for n in D['nodes'] if n.get('id') == 'reception'][0]

man = {}
if os.path.exists(MANIFEST):
    man = json.load(open(MANIFEST, encoding='utf-8'))

todo, done = [], []
for pg in nd['pages']:
    vo = pg.get('vo')
    if not vo:
        continue
    key = pg.get('who') or 'narr'
    if key not in VOICES:
        key = 'narr'
    name = os.path.basename(vo)[:-4]
    dst = os.path.join(OUTDIR, name + '.mp3')
    have = man.get(vo, {}).get('voice')
    if have == key and os.path.exists(dst) and os.path.getsize(dst) > 2000:
        done.append(name)
        continue
    todo.append((vo, name, key, pg['tx'].strip()))

chars = {}
for _, _, key, tx in todo:
    chars[key] = chars.get(key, 0) + len(tx)
cost = sum(len(tx) * VOICES[key][2] / 1000 for _, _, key, tx in todo)
print('страниц: %d, к переозвучке: %d, уже в нужном голосе: %d'
      % (len(nd['pages']), len(todo), len(done)))
for k, n in sorted(chars.items(), key=lambda x: -x[1]):
    print('  %-10s %5d зн.  ~%.2f ₽  (%s)'
          % (k, n, n * VOICES[k][2] / 1000, VOICES[k][0]))
print('смета: ~%.2f ₽' % cost)
if DRY or not todo:
    sys.exit(0)

spent = 0.0
for vo, name, key, tx in todo:
    if spent >= CAP_RUB:
        print('STOP: cap %.0f ₽' % CAP_RUB); break
    model, opts, _ = VOICES[key]
    say = re.sub(r'^[\u2014\u2013-]+\s*', '', tx)
    say = re.sub(r'\s+', ' ', say)
    try:
        files, st = pv.generate_to_files(model, say, opts, outdir=OUTDIR,
                                         name=name, max_price_rub=8)
        got = files[0]
        dst = os.path.join(OUTDIR, name + '.mp3')
        tmp = dst + '.tmp.mp3'
        r = subprocess.run([FF, '-y', '-i', got, '-ar', '44100', '-ac', '1',
                            '-b:a', '96k', tmp], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError('ffmpeg: ' + r.stderr[-200:])
        os.replace(tmp, dst)
        if os.path.abspath(got) != os.path.abspath(dst) and os.path.exists(got):
            os.remove(got)
        price = float(st.get('priceRub') or 0)
        spent += price
        man[vo] = {'voice': key, 'model': model, 'chars': len(say),
                   'price': price}
        json.dump(man, open(MANIFEST, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print('  OK %-8s %-10s %4d зн.  %.2f ₽' % (name, key, len(say), price))
    except Exception as e:
        print('  FAIL %s (%s): %s' % (name, key, e))

print('итого %.2f ₽' % spent)
