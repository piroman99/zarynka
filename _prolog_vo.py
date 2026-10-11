# -*- coding: utf-8 -*-
"""ЗАКАДР ПРОЛОГА — голос Charon (gemini-3.8-flash-tts), по сегментам S1..S6.
Сегмент = один кадр раскадровки. Тайминг кадров подгоняем под длительность озвучки.
Выход: assets/audio/vo_prolog/s1..s6.mp3 + report.json
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv
from prolog_script import SEG

VOICE = {"gemini_voice": "Charon", "engine": "flash",
         "style_instructions": "спокойный зрелый мужской закадр, размеренно, лёгкая ирония, кинохроника"}

OUTDIR = "assets/audio/vo_prolog"
os.makedirs(os.path.join(HERE, OUTDIR), exist_ok=True)

total_chars = sum(len(t) for _, t, _ in SEG)
print("сегментов:", len(SEG), "| знаков всего:", total_chars,
      "| оценка:", round(total_chars * 1.7 / 1000, 2), "₽\n")

rep = []
for frame, text, name in SEG:
    try:
        files, st = pv.generate_to_files("gemini-3.8-flash-tts", text, VOICE,
                                         outdir=OUTDIR, name=name, max_price_rub=10)
        rep.append({"frame": frame, "file": os.path.relpath(files[0], HERE),
                    "chars": len(text), "price": st.get("priceRub")})
        print(f"  OK {frame} ({name}): {len(text)} зн.  {st.get('priceRub')} ₽ -> {os.path.relpath(files[0], HERE)}")
    except Exception as e:
        print(f"  FAIL {frame}: {e}")

with open(os.path.join(HERE, OUTDIR, "report.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=2)
print("\nсумма ~%.2f ₽" % sum(r["price"] or 0 for r in rep))
