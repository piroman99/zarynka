# -*- coding: utf-8 -*-
"""Прослушка голосов Старика / Сергея / Екатерины.

Генерит по 3 кандидата на роль (gemini-3.8-flash-tts, 1.70 ₽/1000 зн.),
склеивает в один mp3 на роль с паузами 0.6 с между вариантами.

Запуск:  python3 _vo_audition.py quote   # только смета, без генерации
         python3 _vo_audition.py gen
"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg',
                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
OUT = 'assets/audio/audition'

ROLES = {
    'starik': {
        'line': 'Сережа, вы мне опять устраиваете клоунаду. Вам наверняка надо сходить '
                'и помочь нашему цирку.',
        'style': ('Пожилой мужчина 63 года, большой начальник. Говорит негромко, веско и властно, '
                  'с усталой строгостью и насмешливым прищуром. Без крика и без пафоса, '
                  'дикция чёткая, между фразами короткие паузы.'),
        'voices': ['Algenib', 'Orus', 'Fenrir'],
    },
    'sergey': {
        'line': 'Да нет, замечаний не будет. Мы не корректируем программы кандидатов.',
        'style': ('Мужчина 42 года, инженер. Усталый, добродушный, говорит живо и по-деловому, '
                  'с лёгкой иронией, без пафоса и без заискивания. Обычный разговорный темп.'),
        'voices': ['Iapetus', 'Achird', 'Umbriel'],
    },
    'kate': {
        'line': 'Но на орбитальную станцию летали люди старше меня. Я смотрела в сети, '
                'все было хорошо, никаких ограничений для них не было.',
        'style': ('Пожилая женщина 68 лет. Мягкий, тёплый, мелодичный голос, спокойный и достойный. '
                  'Говорит не спеша, с доброй усмешкой, без старческой дрожи и без жалобных ноток.'),
        'voices': ['Gacrux', 'Sulafat', 'Vindemiatrix'],
    },
}


def opts(v, style):
    return {'gemini_voice': v, 'engine': 'flash', 'style_instructions': style}


def ff(args):
    r = subprocess.run([FF] + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError('ffmpeg: ' + r.stderr[-300:])
    return r


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'quote'
    total = 0
    for rk, spec in ROLES.items():
        n = len(spec['line']) * len(spec['voices'])
        total += n
        print('%-7s %-28s %3d зн.  %.2f ₽' % (rk, ', '.join(spec['voices']), n, n * 1.70 / 1000))
    print('ИТОГО %d зн. ~ %.2f ₽' % (total, total * 1.70 / 1000))
    if mode != 'gen':
        return
    print('balance', pv.balance().get('balance_rub'))
    os.makedirs(os.path.join(HERE, OUT), exist_ok=True)
    for rk, spec in ROLES.items():
        parts = []
        for v in spec['voices']:
            print('==', rk, v)
            files, st = pv.generate_to_files('gemini-3.8-flash-tts', spec['line'],
                                             opts(v, spec['style']),
                                             outdir=OUT, name='%s_%s' % (rk, v), max_price_rub=6)
            src = files[0]
            mp3 = os.path.join(HERE, OUT, '%s_%s.mp3' % (rk, v))
            ff(['-y', '-i', src, '-ar', '44100', '-ac', '1', '-b:a', '96k', mp3])
            if os.path.abspath(src) != os.path.abspath(mp3) and os.path.exists(src):
                os.remove(src)
            print('   %.2f ₽ -> %s' % (float(st.get('priceRub') or 0), os.path.relpath(mp3, HERE)))
            parts.append(mp3)
        # склейка с паузами
        sil = os.path.join(HERE, OUT, '_sil.mp3')
        ff(['-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', '0.6', '-b:a', '96k', sil])
        lst = os.path.join(HERE, OUT, '_%s.txt' % rk)
        with open(lst, 'w') as f:
            for i, p in enumerate(parts):
                if i:
                    f.write("file '%s'\n" % sil.replace("'", "'\\''"))
                f.write("file '%s'\n" % p.replace("'", "'\\''"))
        joined = os.path.join(HERE, OUT, 'audition_%s.mp3' % rk)
        ff(['-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', joined])
        print('   склейка ->', os.path.relpath(joined, HERE),
              os.path.getsize(joined), 'B')


if __name__ == '__main__':
    main()
