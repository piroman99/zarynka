# -*- coding: utf-8 -*-
"""ТЕСТ МУЖСКОГО ГОЛОСА рассказчика пролога.
Одна фраза автора — на 4 голосах РАЗНЫХ движков, для выбора на слух.
Ориентир: ~2 ₽ (qwen/gemini) + дорогой elevenlabs как эталон.
Выход: assets/audio/vo_test/<движок>_<голос>.mp3
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

PHRASE = (
    "Кто бросил клич «Марс — дело общее»? Этот вопрос долго интересовал часть "
    "работников Звёздного городка. Очень уж хотелось поймать этого умника "
    "в тёмной подворотне."
)
OUTDIR = "assets/audio/vo_test"

# (движок, голос-params, ярлык)
TEST = [
    ("gpt-4o-mini-tts", {"voice": "onyx", "response_format": "mp3",
                         "instructions": "спокойно, иронично, размеренно, как кинохроника"},
     "gpt_onyx"),
    ("gemini-3.8-flash-tts", {"gemini_voice": "Charon", "engine": "flash",
                              "style_instructions": "спокойный зрелый мужской закадр, ирония"},
     "gemini_charon"),
    ("qwen3-tts", {"voice": "Uncle_Fu", "language": "ru",
                   "instruct": "спокойно, размеренно, с лёгкой иронией"},
     "qwen_unclefu"),
    ("elevenlabs-v4-tts", {"voice": "Roger", "language_code": "ru", "engine": "v4"},
     "elv_roger"),
]

print("фраза:", len(PHRASE), "знаков\n")
os.makedirs(os.path.join(HERE, OUTDIR), exist_ok=True)
report = []
for model, opts, label in TEST:
    try:
        q = pv.price(model, PHRASE, opts)
        print(f"[{label}] {model} quote = {q.get('priceRub')} ₽")
    except Exception as e:
        print(f"[{label}] {model} quote ERROR {e}")

print("\n--- генерация ---")
for model, opts, label in TEST:
    try:
        files, st = pv.generate_to_files(model, PHRASE, opts, outdir=OUTDIR,
                                         name=label, max_price_rub=5)
        report.append({"label": label, "model": model, "voice": opts.get("voice") or opts.get("gemini_voice"),
                       "file": os.path.relpath(files[0], HERE), "price": st.get("priceRub")})
        print(f"  OK {label}: {os.path.relpath(files[0], HERE)}  {st.get('priceRub')} ₽")
    except Exception as e:
        print(f"  FAIL {label}: {e}")

with open(os.path.join(HERE, OUTDIR, "report.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
total = sum(r["price"] or 0 for r in report)
print(f"\nитого файлов: {len(report)}, сумма ~{total:.2f} ₽")
