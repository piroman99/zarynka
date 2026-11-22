# -*- coding: utf-8 -*-
"""Параметры suno (музыка) и MiniMax-Hailuo-02 (i2v) — что можно задать."""
import json, pv


def dump(m):
    try:
        c = pv.capabilities(m)
    except Exception as e:
        print(m, "ERR", e); return
    print("=" * 68, "\n", m, "| kind:", c.get("kind"), "| status:", c.get("status"))
    for op in c.get("operations", []):
        props = op.get("requestJsonSchema", {}).get("properties", {}) or {}
        print(" op:", op.get("id"), "|", (op.get("label") or "")[:70])
        for k, v in (props.get("opts", {}).get("properties", {}) or {}).items():
            enum = v.get("enum")
            print(f"    {k}: {v.get('type')} {('enum=' + str(enum)) if enum else (v.get('description','') or '')[:70]}")
        top = [k for k in props.keys() if k not in ("opts", "model", "strict", "quote_id", "max_price_rub", "webhook_url")]
        if top:
            print("    top-level:", top)


for m in ("suno", "MiniMax-Hailuo-02"):
    dump(m)
