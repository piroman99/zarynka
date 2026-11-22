# -*- coding: utf-8 -*-
"""B+C для сцены «аллея» (решение Ивана 2026-11-10: «по звуку B+C»).

Почему перегенерация, а не перебаланс (замер `_alley_band.py`):
  alley_amb — 22 с петля, 89 % энергии выше 2 кГц, ниже 250 Гц почти пусто: это шипение,
              а не улица; «нет ощущения открытого пространства», «что-то приземлённое»;
  alley_bed — 46 % энергии в 250–800 Гц, 10 % ниже 80 Гц, выше 2 кГц 1.1 %: глухая, басовая.

Новые материалы:
  alley2_amb — elevenlabs-sound-effects-v2, 22 с петля (максимум модели): ветер в елях,
               далёкие птицы, эхо между корпусами, без близких звуков и без низкого гула;
               в 44 с разворачиваем приёмом «вперёд + назад» — шов не слышен;
  alley2_bed — lyria-3-5: светлая тема, меньше баса, больше воздуха, 72 bpm.
Затем микс с правильным балансом (амбиент под темой, срез низа и шипения).

Запуск: python3 _alley_audio2.py [amb bed] [--dry]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pv  # noqa: E402

OUT = 'assets/audio/sketch'

AMB_PROMPT = (
    "Wide open spring park alley ambience, airy and spacious: light wind in tall spruce "
    "branches, distant birdsong, faint echo between far buildings, gentle melting-snow "
    "drips far away. No close sounds, no voices, no music, no low rumble, no bass hum, "
    "no hiss. Bright, calm, transparent, deep open space, quiet scene background"
)
BED_PROMPT = (
    "light airy spring morning instrumental for a park scene: soft felt piano, delicate high "
    "strings, a hint of wooden flute, hopeful and shy mood, spacious and open, thin and "
    "transparent texture, no low bass, no drums, no percussion, slow tempo, unhurried, "
    "loopable background theme, purely instrumental, no vocals"
)

want = [a for a in sys.argv[1:] if not a.startswith('-')] or ['amb', 'bed']
dry = '--dry' in sys.argv

jobs = []
if 'amb' in want:
    jobs.append(('alley2_amb', 'elevenlabs-sound-effects-v2', AMB_PROMPT,
                 {'duration': '22', 'loop': True, 'prompt_influence': 0.6,
                  'output_format': 'mp3_hq'}))
if 'bed' in want:
    jobs.append(('alley2_bed', 'lyria-3-5', BED_PROMPT,
                 {'title': 'Аллея, открытый воздух', 'bpm': 72}))

for name, model, prompt, opts in jobs:
    try:
        q = pv.price(model, prompt, opts)
        print('[quote] %-11s %s RUB (%s)' % (name, q.get('priceRub'), model), flush=True)
    except Exception as e:  # noqa: BLE001
        print('[quote-fail] %-11s %s' % (name, str(e)[:160]), flush=True)
        q = None
    if dry:
        continue
    try:
        files, st = pv.generate_to_files(model, prompt, opts, outdir=OUT, name=name,
                                         max_price_rub=15)
        print('[ok] %-11s %s' % (name, [os.path.basename(f) for f in files]), flush=True)
    except Exception as e:  # noqa: BLE001
        print('[fail] %-11s %s' % (name, str(e)[:200]), flush=True)
