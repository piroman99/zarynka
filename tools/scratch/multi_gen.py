# -*- coding: utf-8 -*-
"""Прогон одного промпта через несколько моделей — для сравнения, кто лучше «старит»."""
import os, sys, time, json
import gen, pv

HERE = os.path.dirname(os.path.abspath(gen.__file__))

MODELS = sys.argv[1].split(",") if len(sys.argv) > 1 else [
    "gpt-image-2", "nano-banana-2", "qwen3-image", "grok-imagine", "flux-2",
]
NAME = sys.argv[2] if len(sys.argv) > 2 else "sergey_eng_old"
REF = sys.argv[3] if len(sys.argv) > 3 else "assets/sprites/sergey.png"

spec = gen.SCENES[NAME]
prompt = spec["prompt"] + "\n\nСТИЛЬ: " + gen.STYLE
base_opts = {"aspect_ratio": spec.get("aspect", "3:4"), "resolution": spec.get("res", "1K")}

report = []
outdir = os.path.join(HERE, "assets", "gen")
for m in MODELS:
    opts = dict(base_opts)
    ref_used = None
    # референс пробуем только у моделей, которые умеют image-to-image
    if m in ("gpt-image-2", "nano-banana-2", "nano-banana", "qwen3-image", "flux-2",
             "seedream-5", "seedream-4-5", "grok-imagine") and os.path.exists(os.path.join(HERE, REF)):
        opts["image_base64"] = gen.b64(os.path.join(HERE, REF))
        ref_used = REF
    t0 = time.time()
    try:
        q = pv.price(m, prompt, opts)
        files, st = pv.generate_to_files(m, prompt, opts, outdir="assets/gen",
                                         name=f"{NAME}__{m}", max_price_rub=12)
        dt = round(time.time() - t0)
        rec = {"model": m, "price": st.get("priceRub"), "sec": dt,
               "ref": ref_used, "file": os.path.relpath(files[0], HERE)}
        print(f"[OK] {m:16s} {rec['price']} ₽  {dt}s  -> {rec['file']}")
    except Exception as e:
        dt = round(time.time() - t0)
        rec = {"model": m, "error": str(e)[:200], "sec": dt, "ref": ref_used}
        print(f"[FAIL] {m:16s} {dt}s  {str(e)[:140]}")
    report.append(rec)

p = os.path.join(HERE, "assets", "gen", f"_{NAME}_report.json")
json.dump(report, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("report:", os.path.relpath(p, HERE))
