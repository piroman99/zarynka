# -*- coding: utf-8 -*-
"""A/B голоса ЗАКАДРА: тот же текст и та же подача, разные голоса gemini.
Закадр сейчас = Charon, то есть ТОТ ЖЕ голос, что у Сергея, — на длинных
описаниях кажется, что «всё читает Сергей». Здесь 3 альтернативы + текущий.

  python3 _narr_ab.py          # синтез + склейка
"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries',
                  'ffmpeg-linux-x86_64-v7.0.2')
OUT = os.path.join(HERE, 'assets', 'audio', 'narr_ab')
os.makedirs(OUT, exist_ok=True)

TEXT = ('Так и пришлось долгих два месяца сидеть на собеседованиях, '
        'принимать документы и мечтать вернуться к нормальной работе.')

STYLE = (
    "Спокойный, зрелый мужской закадровый голос. Документальная кинохроника: "
    "серьёзно, сдержанно, ровно, без иронии, без насмешки и без пафоса. "
    "Говори не спеша, чуть медленнее обычного, с небольшими паузами между фразами. "
    "Нейтральная чёткая дикция, доверительная интонация рассказчика."
)

VOICES = [('00_charon_текущий', 'Charon'),
          ('01_orus', 'Orus'),
          ('02_alnilam', 'Alnilam'),
          ('03_iapetus', 'Iapetus')]

files = []
for tag, v in VOICES:
    opts = {'gemini_voice': v, 'engine': 'flash', 'style_instructions': STYLE}
    try:
        got, st = pv.generate_to_files('gemini-3.8-flash-tts', TEXT, opts,
                                       outdir=OUT, name=tag, max_price_rub=3)
        f = got[0]
        dst = os.path.join(OUT, tag + '.mp3')
        if os.path.abspath(f) != os.path.abspath(dst):
            subprocess.run([FF, '-y', '-i', f, '-ar', '44100', '-ac', '1',
                            '-b:a', '96k', dst], capture_output=True, text=True)
            os.remove(f)
        files.append(dst)
        print('OK', tag, st.get('priceRub'), '₽')
    except Exception as e:
        print('FAIL', tag, e)

# склейка с паузами 0.9 с
lst = os.path.join(OUT, '_list.txt')
with open(lst, 'w', encoding='utf-8') as fh:
    for f in files:
        fh.write("file '%s'\n" % f.replace("'", "'\\''"))
sil = os.path.join(OUT, '_sil.mp3')
subprocess.run([FF, '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-t', '0.9', '-b:a', '96k', sil], capture_output=True, text=True)
with open(lst, 'w', encoding='utf-8') as fh:
    for i, f in enumerate(files):
        if i:
            fh.write("file '%s'\n" % sil)
        fh.write("file '%s'\n" % f)
mont = os.path.join(OUT, 'montage_narr.mp3')
subprocess.run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', lst,
                '-b:a', '96k', mont], capture_output=True, text=True)
print('MONTAGE', mont, os.path.getsize(mont))
print('порядок:', [os.path.basename(f) for f in files])
