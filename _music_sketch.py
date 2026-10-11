# -*- coding: utf-8 -*-
"""МУЗЫКАЛЬНЫЕ СКЕТЧИ для «Зарянки» — lyria-3-5 (8.13 ₽/трек, дешевле suno 10.82).
3 темы × 1 скетч ≈ 24.4 ₽ (в лимит 12–25 ₽).
  • Приёмная / Земля  — тёплая ностальгическая, советский ретро
  • Пролог-хроника    — иронично-хроникальная мини-тема
  • Космос            — холодный синтезатор, пэды + арпеджио
Запуск: python3 _music_sketch.py [имя|all]   (по умолчанию all)
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

OUTDIR = "assets/audio/sketch"
TRACKS = {
    "vn_reception": (
        "Приёмная (тёплая)",
        "warm nostalgic instrumental, gentle Soviet retro flavor, delicate acoustic piano "
        "and nylon-string guitar, a touch of accordion, affectionate light irony, calm mid "
        "tempo, cozy and soft, loopable background theme for a visual novel, purely "
        "instrumental, no vocals, not epic, no heavy drums",
        92),
    "prolog_chronicle": (
        "Пролог-хроника",
        "quirky documentary newsreel instrumental, ironic retro chronicle feel, muted brass, "
        "pizzicato strings, light woodwinds, subtle brushes, 1960s archival tone, mid tempo, "
        "understated and playful, background for narration, purely instrumental, no vocals",
        104),
    "vn_space": (
        "Космос (холодный)",
        "cold ambient synth instrumental, spacious evolving pads, slow arpeggio, deep space, "
        "distant and airy, subtle heartbeat pulse, restrained and cinematic, lunar "
        "atmosphere, purely instrumental, no vocals, no heavy drums, seamless loop",
        70),
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
        print(f"[{name}] lyria quote = {q.get('priceRub')} ₽")
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

p = os.path.join(HERE, OUTDIR, "report.json")
old = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else []
seen = {r["name"] for r in report}
old = [r for r in old if r["name"] not in seen] + report
json.dump(old, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\nитого новых: {len(report)}, сумма ~{sum(r['price'] or 0 for r in report):.2f} ₽")
