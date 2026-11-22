# -*- coding: utf-8 -*-
"""Дамп opts-схемы: как передавать референс и какие есть ручки."""
import json, pv

def dump(m):
    c = pv.capabilities(m)
    print("=" * 70, "\n", m)
    for op in c.get("operations", []):
        props = (op.get("requestJsonSchema", {}).get("properties", {}) or {})
        opts = props.get("opts", {}).get("properties", {}) or {}
        print(" op:", op.get("id"))
        for k, v in opts.items():
            print(f"   {k}: {v.get('type')} {v.get('enum') or v.get('description','') or ''}"[:160])

for m in ("flux-2", "nano-banana-2.1", "nano-banana-2"):
    dump(m)
