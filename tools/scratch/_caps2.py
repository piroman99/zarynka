# -*- coding: utf-8 -*-
"""Полная схема opts для MiniMax-Hailuo-02."""
import json, pv

c = pv.capabilities("MiniMax-Hailuo-02")
op = c["operations"][0]
props = op["requestJsonSchema"]["properties"]
print("TOP-LEVEL KEYS:", list(props.keys()))
print()
print(json.dumps(props.get("opts"), ensure_ascii=False, indent=2)[:4000])
