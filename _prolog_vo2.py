# -*- coding: utf-8 -*-
"""ЗАКАДР ПРОЛОГА v2 — тот же голос Charon, но БЕЗ иронии, ровная кинохроника.
Исправление по замечанию заказчика: v1 («лёгкая ирония») звучал издевательски.
Выход: assets/audio/vo_prolog2/s1..s6.mp3 + report.json
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv
from prolog_script import SEG

VOICE = {
    "gemini_voice": "Charon", "engine": "flash",
    "style_instructions": (
        "Спокойный, зрелый мужской закадровый голос. Документальная кинохроника: "
        "серьёзно, сдержанно, ровно, без иронии, без насмешки и без пафоса. "
        "Говори не спеша, чуть медленнее обычного, с небольшими паузами между фразами. "
        "Нейтральная чёткая дикция, доверительная интонация рассказчика."
    ),
}

OUTDIR = "assets/audio/vo_prolog2"
os.makedirs(os.path.join(HERE, OUTDIR), exist_ok=True)

total_chars = sum(len(t) for _, t, _ in SEG)
print("сегментов:", len(SEG), "| знаков:", total_chars,
      "| оценка ~%.2f ₽" % (total_chars * 1.7 / 1000))

rep = []
for frame, text, name in SEG:
    try:
        files, st = pv.generate_to_files("gemini-3.8-flash-tts", text, VOICE,
                                         outdir=OUTDIR, name=name, max_price_rub=10)
        rep.append({"frame": frame, "file": os.path.relpath(files[0], HERE),
                    "chars": len(text), "price": st.get("priceRub")})
        print(f"  OK {frame} ({name}): {len(text)} зн.  {st.get('priceRub')} ₽")
    except Exception as e:
        print(f"  FAIL {frame}: {e}")

with open(os.path.join(HERE, OUTDIR, "report.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=2)
print("сумма ~%.2f ₽" % sum(r["price"] or 0 for r in rep))
