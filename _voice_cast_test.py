# -*- coding: utf-8 -*-
"""Тест голосов Приёмной: по 3-4 кандидата на персонажа, каждая реплика —
его же строка из игры. Результат: assets/audio/vo_cast/<who>_<voice>.mp3
+ склейка montage_<who>.mp3 для прослушки.

Запуск: python3 _voice_cast_test.py            (все персонажи)
        python3 _voice_cast_test.py starik     (только один)
"""
import os, sys, json, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg',
                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
OUT = 'assets/audio/vo_cast'
os.makedirs(os.path.join(HERE, OUT), exist_ok=True)

# реплика-образец = самая длинная «чистая» строка персонажа из игры
LINES = {
    'starik': ('Старик',
               'Сережа, вы мне опять устраиваете клоунаду. Вам наверняка надо '
               'сходить и помочь нашему цирку.',
               'Старый, очень немолодой мужчина. Голос сухой, низкий, устало-'
               'начальственный. Говорит негромко, но веско, с раздражением, '
               'которое он не повышает. Без театральности, без пафоса.'),
    'sergey': ('Сергей',
               'Да, конечно, текущее состояние у вас удовлетворительное. Однако '
               'в экспедиции предполагаются существенные нагрузки, тяжелые даже '
               'для совершенно здоровых молодых людей.',
               'Мужчина около шестидесяти, инженер, много лет на службе. Голос '
               'спокойный, ровный, вежливо-официальный, немного усталый. '
               'Чёткая дикция, доброжелательно, но сдержанно. Без иронии.'),
    'kate': ('Екатерина',
             'Но на орбитальную станцию летали люди старше меня. Я смотрела в '
             'сети, все было хорошо, никаких ограничений для них не было.',
             'Женщина около пятидесяти. Голос мягкий, мелодичный, живой и '
             'спокойный, с достоинством. Говорит тепло, но уверенно, без '
             'кокетства и без жалобы.'),
}

CAND = {
    'starik': ['Fenrir', 'Orus', 'Iapetus', 'Algenib'],
    'sergey': ['Charon', 'Schedar', 'Umbriel', 'Achird'],
    'kate':   ['Kore', 'Leda', 'Aoede', 'Callirrhoe'],
}

CAP_RUB = 12.0
spent = 0.0
report = []
want = sys.argv[1:] or list(CAND)
for key in want:
    who, line, style = LINES[key]
    for voice in CAND[key]:
        if spent >= CAP_RUB:
            print('STOP: cap %.0f' % CAP_RUB); break
        name = '%s_%s' % (key, voice.lower())
        dst = os.path.join(HERE, OUT, name + '.mp3')
        if os.path.exists(dst) and os.path.getsize(dst) > 2000:
            print('  skip', name); continue
        opts = {'gemini_voice': voice, 'engine': 'flash',
                'style_instructions': style}
        try:
            files, st = pv.generate_to_files('gemini-3.8-flash-tts', line, opts,
                                             outdir=OUT, name=name,
                                             max_price_rub=6)
        except Exception as e:
            print('  FAIL %s: %s' % (name, e)); continue
        got = files[0]
        tmp = dst + '.tmp.mp3'
        r = subprocess.run([FF, '-y', '-i', got, '-ar', '44100', '-ac', '1',
                            '-b:a', '96k', tmp], capture_output=True, text=True)
        if r.returncode != 0:
            print('  ffmpeg FAIL', r.stderr[-200:]); continue
        os.replace(tmp, dst)
        price = float(st.get('priceRub') or 0)
        spent += price
        print('  ok %-18s %s  %.2f ₽' % (name, voice, price))
        report.append({'who': who, 'key': key, 'voice': voice,
                       'file': OUT + '/' + name + '.mp3', 'price': price})

json.dump(report, open(os.path.join(HERE, OUT, 'report.json'), 'w'),
          ensure_ascii=False, indent=2)
print('итого %.2f ₽' % spent)
