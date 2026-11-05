# -*- coding: utf-8 -*-
"""Музыка/озвучка для сцены «аллея» (правка Ивана 2026-11-05, пункт 5).

Сейчас сцена играет на приёмной теме (`music: reception`) — Иван: «может уже другую музыку
для этой сцены или озвучку весенней улицы». Делаю два материала:
  • alley_amb  — фон spring-улицы (elevenlabs-sound-effects-v2, петля 22 с, 5.96 ₽);
  • alley_bed  — тёплая весенняя тема (lyria-3-5, ~8.13 ₽);
плюс микс `alley_bed_mix` (тема + улица под ней, ffmpeg) — чтобы Иван выбрал букву.

Запуск: python3 _alley_audio.py [amb|bed|mix] [--dry]
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv  # noqa: E402

WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
OUT = 'assets/audio/sketch'

AMB_PROMPT = (
    "Spring park alley ambience, no music, no voices: water dripping from melting snow, "
    "wet asphalt, distant birdsong, soft wind moving through tall spruce trees, "
    "faint footsteps far away, calm and airy, quiet background for a visual novel scene"
)
BED_PROMPT = (
    "warm spring morning instrumental, gentle acoustic piano with soft nylon guitar, "
    "light airy strings, hopeful and shy mood, unhurried, tender, loopable background theme "
    "for a visual novel scene in a park, purely instrumental, no vocals, no heavy drums"
)


def gen():
    jobs = []
    if 'amb' in want:
        jobs.append(('alley_amb', 'elevenlabs-sound-effects-v2', AMB_PROMPT,
                     {'duration': '22', 'loop': True, 'prompt_influence': 0.55,
                      'output_format': 'mp3'}))
    if 'bed' in want:
        jobs.append(('alley_bed', 'lyria-3-5', BED_PROMPT,
                     {'title': 'Весенняя аллея', 'bpm': 76}))
    for name, model, prompt, opts in jobs:
        q = pv.price(model, prompt, opts)
        print('[quote] %-10s %s RUB (%s)' % (name, q.get('priceRub'), model), flush=True)
        if dry:
            continue
        try:
            files, st = pv.generate_to_files(model, prompt, opts, outdir=OUT, name=name,
                                             max_price_rub=12)
            print('[ok] %-10s %s' % (name, [os.path.basename(f) for f in files]), flush=True)
        except Exception as e:  # noqa: BLE001
            print('[fail] %-10s %s' % (name, str(e)[:160]), flush=True)


def mix():
    """Тема + улица под ней: улица на -13 dB, фейды 2 с, длина по теме."""
    import glob
    beds = sorted(glob.glob(os.path.join(HERE, OUT, 'alley_bed_0.*')))
    ambs = sorted(glob.glob(os.path.join(HERE, OUT, 'alley_amb_0.*')))
    if not (beds and ambs):
        print('mix SKIP: нет материалов')
        return
    bed, amb = beds[0], ambs[0]
    dst = os.path.join(HERE, OUT, 'alley_bed_mix_0.mp3')
    fc = ("[1:a]aloop=loop=-1:size=2e9,atrim=0:60,volume=0.22,afade=t=in:st=0:d=2[amb];"
          "[0:a][amb]amix=inputs=2:duration=first:dropout_transition=0,volume=1.5[m]")
    r = subprocess.run([FF, '-y', '-i', bed, '-i', amb, '-filter_complex', fc,
                        '-map', '[m]', '-c:a', 'libmp3lame', '-b:a', '160k', dst],
                       capture_output=True, text=True)
    print('mix rc', r.returncode, os.path.exists(dst) and os.path.getsize(dst))
    if r.returncode:
        print(r.stderr[-600:])


def finals():
    """Три варианта для Ивана в 112 kbps (тяжёлый mp4-под исходник в игру не идёт).

      alley_amb.mp3  — только весенняя улица (петля 22 с);
      alley_bed.mp3  — только тема;
      alley_mix.mp3  — тема + улица под ней (поставлен в сцену по умолчанию).
    """
    import glob
    pairs = [('alley_mix.mp3', glob.glob(os.path.join(HERE, OUT, 'alley_bed_mix_0.*'))),
             ('alley_bed.mp3', glob.glob(os.path.join(HERE, OUT, 'alley_bed_0.*'))),
             ('alley_amb.mp3', glob.glob(os.path.join(HERE, OUT, 'alley_amb_0.*')))]
    for name, srcs in pairs:
        if not srcs:
            continue
        dst = os.path.join(HERE, OUT, name)
        r = subprocess.run([FF, '-y', '-i', srcs[0], '-c:a', 'libmp3lame', '-b:a', '112k',
                            '-ac', '2', dst], capture_output=True, text=True)
        print('%-14s rc=%d %6.0f КБ' % (name, r.returncode,
                                        os.path.getsize(dst) / 1024 if os.path.exists(dst) else 0))


dry = '--dry' in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith('-')]
want = set(args) if args else {'amb', 'bed'}
if want & {'amb', 'bed'}:
    gen()
if (not args or 'mix' in want) and not dry:
    mix()
if not dry:
    finals()
for n in ('alley_amb_0.mp3', 'alley_bed_0.mp4', 'alley_bed_mix_0.mp3'):
    p = os.path.join(HERE, OUT, n)
    if os.path.exists(p):
        d = subprocess.run([FF, '-hide_banner', '-i', p], capture_output=True, text=True).stderr
        ln = [l.strip() for l in d.splitlines() if 'Duration' in l]
        print('%-20s %6.0f КБ  %s' % (n, os.path.getsize(p) / 1024, ln[0][:34] if ln else ''))
