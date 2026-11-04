# -*- coding: utf-8 -*-
"""Только котировки (ничего не генерирует)."""
import _cg_sad as C
import gen, pv

for name, prompt in C.SCENES.items():
    opts = {"aspect_ratio": "16:9", "resolution": "1K", "image_base64": C.b64s(C.REF_KATE)}
    for model in ("gpt-image-2", "nano-banana-2.1"):
        try:
            q = pv.price(model, prompt, opts)
            print("%-10s %-18s %s RUB" % (name, model, q.get("priceRub")))
        except Exception as e:
            print("%-10s %-18s ERR %s" % (name, model, str(e)[:150]))
