# -*- coding: utf-8 -*-
"""ПЕРЕДЕЛКА музыки: Приёмная/Земля + Пролог-хроника.
Заказчик: прежние «вообще не в тему», нужно МЕНЕЕ РАЗДРАЖАЮЩЕЕ и НЕНАВЯЗЧИВОЕ.
Космос (vn_space) — одобрен, НЕ трогаем.
Даю по 2 варианта на тему. lyria-3-5 = 8.13 ₽/трек → 4 трека ≈ 32.5 ₽.
Выход: assets/audio/sketch/<name>_0.mp4
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

OUTDIR = "assets/audio/sketch"
TRACKS = {
    # --- Приёмная / Земля: очень тихая, минимальная, фон для чтения ---
    "vn_reception_soft": (
        "Приёмная — мягкая (A)",
        "very soft minimal ambient piano, sparse single felt-piano notes with long silences, "
        "warm quiet pad underneath, no melody hooks, no drums, no accordion, no brass, "
        "unobtrusive calm background bed for reading, slow and meditative, low-key, "
        "seamless loop, purely instrumental, no vocals", 72),
    "vn_reception_lullaby": (
        "Приёмная — колыбельная (B)",
        "gentle felt-piano lullaby with very soft warm strings, tender and quiet, minimal "
        "arrangement, subtle nostalgic warmth, no percussion, no accordion, no brass, "
        "understated underscore for a visual novel, purely instrumental, no vocals, "
        "even and unobtrusive", 66),
    # --- Пролог-хроника: нейтральный тихий фон под закадр, без иронии-оркестра ---
    "prolog_bed_soft": (
        "Пролог — тихий фон (A)",
        "subtle neutral documentary underscore, soft muted strings and light felt piano, "
        "minimal and quiet, understated, no brass, no pizzicato, no drums, no melody hooks, "
        "even background bed for spoken narration, slow, purely instrumental, no vocals, "
        "unobtrusive", 80),
    "prolog_bed_ambient": (
        "Пролог — эмбиент-фон (B)",
        "gentle ambient underscore, soft mallet and piano textures over a warm low pad, calm "
        "and unobtrusive, minimal, faint nostalgic tint without irony, no percussion, "
        "background bed for spoken narration, purely instrumental, no vocals, steady and even",
        76),
}

which = sys.argv[1] if len(sys.argv) > 1 else "all"
names = list(TRACKS) if which == "all" else [which]

os.makedirs(os.path.join(HERE, OUTDIR), exist_ok=True)
report = []
for name in names:
    title, style, bpm = TRACKS[name]
    opts = {"title": title, "bpm": bpm}
    try:
        q = pv.price("lyria-3-5", style, opts)
        print(f"[{name}] quote = {q.get('priceRub')} ₽")
    except Exception as e:
        print(f"[{name}] quote ERROR {e}")
    try:
        files, st = pv.generate_to_files("lyria-3-5", style, opts, outdir=OUTDIR,
                                         name=name, max_price_rub=9)
        report.append({"name": name, "title": title,
                       "file": os.path.relpath(files[0], HERE), "price": st.get("priceRub")})
        print(f"  OK {name}: {os.path.relpath(files[0], HERE)}  {st.get('priceRub')} ₽")
    except Exception as e:
        print(f"  FAIL {name}: {e}")

p = os.path.join(HERE, OUTDIR, "report2.json")
json.dump(report, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\nитого новых: {len(report)}, сумма ~{sum(r['price'] or 0 for r in report):.2f} ₽")
