# -*- coding: utf-8 -*-
"""Голосовой тест ЕКАТЕРИНЫ: одна реплика разными голосами -> монтаж."""
import os, sys, subprocess, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

FF = os.path.join(os.path.dirname(HERE), '..', '.probe', '.lib', 'imageio_ffmpeg',
                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
OUT = 'assets/audio/vo_kate'
os.makedirs(os.path.join(HERE, OUT), exist_ok=True)

# дословные строки Кати (#4 и #6 из рассказа)
LINE = ("Вы хотите сказать, что я слишком старая, чтобы лететь в космос? "
        "Но на орбитальную станцию летали люди старше меня.")

STYLE_KATE = ("Пожилая русская женщина, 68 лет. Мягкий, мелодичный, тёплый, немного "
              "усталый голос. Спокойно, с достоинством, с лёгкой грустью, доброжелательно.")

CAND = [
    ('01', 'gemini-3.8-flash-tts', {'gemini_voice': 'Aoede', 'engine': 'flash',
                                    'style_instructions': STYLE_KATE}, 'Джемини · Aoede'),
    ('02', 'gemini-3.8-flash-tts', {'gemini_voice': 'Kore', 'engine': 'flash',
                                    'style_instructions': STYLE_KATE}, 'Джемини · Kore'),
    ('03', 'gemini-3.8-flash-tts', {'gemini_voice': 'Leda', 'engine': 'flash',
                                    'style_instructions': STYLE_KATE}, 'Джемини · Leda'),
    ('04', 'elevenlabs-v4-tts', {'voice': 'Sarah'}, 'ElevenLabs · Sarah'),
    ('05', 'elevenlabs-v4-tts', {'voice': 'Matilda'}, 'ElevenLabs · Matilda'),
    ('06', 'elevenlabs-v4-tts', {'voice': 'Charlotte'}, 'ElevenLabs · Charlotte'),
    ('07', 'qwen3-tts', {'voice': 'Serena'}, 'Qwen · Serena'),
]

LABEL_STYLE = {"gemini_voice": "Charon", "engine": "flash",
               "style_instructions": "Нейтральный диктор, ровно и чётко."}

rep = []
for num, model, opts, label in CAND:
    try:
        files, st = pv.generate_to_files(model, LINE, opts, outdir=OUT,
                                         name='kate_' + num, max_price_rub=6)
        rep.append({'n': num, 'model': model, 'voice': opts.get('voice') or opts.get('gemini_voice'),
                    'label': label, 'file': os.path.relpath(files[0], HERE),
                    'price': st.get('priceRub')})
        print('OK %s  %s  %s ₽' % (num, label, st.get('priceRub')))
    except Exception as e:
        print('FAIL %s: %s' % (num, e))

# подписи «Вариант N» голосом закадрового диктора
for num, *_ in [(c[0],) for c in CAND]:
    pass
for idx, (num, model, opts, label) in enumerate(CAND, 1):
    txt = 'Вариант %d.' % idx
    try:
        files, st = pv.generate_to_files('gemini-3.8-flash-tts', txt, LABEL_STYLE,
                                         outdir=OUT, name='lbl_' + num, max_price_rub=2)
        print('OK label %d' % idx)
    except Exception as e:
        print('FAIL label %d: %s' % (idx, e))

with open(os.path.join(HERE, OUT, 'report.json'), 'w', encoding='utf-8') as f:
    json.dump(rep, f, ensure_ascii=False, indent=2)
print('итого ~%.2f ₽' % sum(float(r['price'] or 0) for r in rep))
