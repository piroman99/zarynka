# -*- coding: utf-8 -*-
"""Пробы голосов для трёх персонажей: по 3 кандидата, реальная реплика.
Итог: assets/review/vo_try_<who>_ABC.mp3 — кандидаты подряд, между ними 0.8 с тишины.
  python3 _vo_pick.py quote     # только смета
  python3 _vo_pick.py gen
"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg',
                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
TMP = os.path.join(HERE, '.tmp_vo')
REV = os.path.join(HERE, 'assets', 'review')

# (голос, стиль) — 3 кандидата на персонажа
CAND = {
    'starik': (
        '— Сережа, вы мне опять устраиваете клоунаду. Вам наверняка надо сходить '
        'и помочь нашему цирку.',
        [('Algenib', 'Пожилой мужчина 63 лет, начальник. Низкий хрипловатый голос, '
                     'суровый и командирский, говорит веско и неторопливо, с '
                     'раздражением, но без крика.'),
         ('Gacrux', 'Пожилой мужчина 63 лет, большой начальник. Зрелый низкий голос, '
                    'устало-жёсткий, ровный, с начальнической иронией и '
                    'недовольством.'),
         ('Alnilam', 'Пожилой мужчина 63 лет, начальник. Твёрдый низкий голос, '
                     'отрывистая деловая манера, холодно и требовательно.')],
    ),
    'sergey': (
        '— Добрый день. Добро пожаловать в Звездный городок.',
        [('Achird', 'Мужчина 42 лет, инженер. Усталый, но приветливый голос, '
                    'с лёгкой самоиронией и дежурной улыбкой.'),
         ('Schedar', 'Мужчина 42 лет, инженер. Ровный спокойный голос, доброжелательный, '
                     'чуть усталый, без нажима.'),
         ('Orus', 'Мужчина 42 лет, инженер. Твёрдый ясный голос, вежливо-деловой, '
                  'сдержанно-дружелюбный.')],
    ),
    'kate': (
        '— Здравствуйте, Сергей, вот, пожалуйста.',
        [('Sulafat', 'Пожилая женщина 68 лет. Тёплый мягкий голос, спокойный и '
                     'приветливый, с достоинством, без старческой дрожи.'),
         ('Vindemiatrix', 'Пожилая женщина 68 лет. Тихий нежный голос, '
                          'доброжелательный и ясный, с мягкой улыбкой.'),
         ('Kore', 'Пожилая женщина 68 лет. Ясный уверенный голос, спокойная '
                  'вежливость и внутренняя сила.')],
    ),
}

cmd = sys.argv[1] if len(sys.argv) > 1 else 'quote'
os.makedirs(TMP, exist_ok=True)
os.makedirs(REV, exist_ok=True)

if cmd == 'quote':
    print('баланс:', pv.balance()['balance_rub'], '₽')
    total = 0.0
    for who, (line, cands) in CAND.items():
        sub = 0.0
        for voice, style in cands:
            opts = {'engine': 'flash', 'gemini_voice': voice, 'style_instructions': style}
            q = pv.price('gemini-3.8-flash-tts', line, opts)
            p = float(q.get('priceRub') or 0)
            sub += p
            print('  %-7s %-12s %3d зн = %.2f ₽' % (who, voice, len(line), p))
        print('  -> %s: %.2f ₽' % (who, sub))
        total += sub
    print('ИТОГО ~%.2f ₽' % total)
    sys.exit(0)

parts = []
for who, (line, cands) in CAND.items():
    segs = []
    for voice, style in cands:
        opts = {'engine': 'flash', 'gemini_voice': voice, 'style_instructions': style}
        name = 'try_%s_%s' % (who, voice)
        files, st = pv.generate_to_files('gemini-3.8-flash-tts', line, opts,
                                         outdir='.tmp_vo', name=name, max_price_rub=6)
        src = files[0]
        dst = os.path.join(TMP, name + '.mp3')
        subprocess.run([FF, '-y', '-i', src, '-ar', '44100', '-ac', '1', '-b:a', '96k', dst],
                       capture_output=True, text=True, check=True)
        if os.path.abspath(src) != os.path.abspath(dst) and os.path.exists(src):
            os.remove(src)
        segs.append(dst)
        print('  OK %-22s %.2f ₽' % (voice, float(st.get('priceRub') or 0)))

    # склейка через 0.8 с тишины
    lst = os.path.join(TMP, 'list_%s.txt' % who)
    sil = os.path.join(TMP, 'sil.mp3')
    if not os.path.exists(sil):
        subprocess.run([FF, '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                        '-t', '0.8', '-b:a', '96k', sil], capture_output=True, check=True)
    with open(lst, 'w', encoding='utf-8') as f:
        for s in segs:
            f.write("file '%s'\n" % s.replace("'", "'\\''"))
            f.write("file '%s'\n" % sil.replace("'", "'\\''"))
    out = os.path.join(REV, 'vo_try_%s_ABC.mp3' % who)
    subprocess.run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', lst,
                    '-b:a', '96k', out], capture_output=True, check=True)
    print('->', os.path.relpath(out, HERE), os.path.getsize(out), 'B')
    parts.append(out)
print('готово:', len(parts))
