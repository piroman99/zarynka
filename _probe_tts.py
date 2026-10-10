# -*- coding: utf-8 -*-
"""Смотрит возможности и цены для TTS и музыки (без генерации)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

for m in ("gpt-4o-mini-tts", "gemini-3.8-flash-tts", "qwen3-tts", "elevenlabs-v4-tts"):
    try:
        cap = pv.capabilities(m)
        params = cap.get("params") or cap.get("opts") or []
        print(f"\n== {m} ==")
        print("  keys:", list(cap.keys()))
        for p in (params if isinstance(params, list) else []):
            print("   -", p.get("key"), "|", p.get("label"), "| type=", p.get("type"),
                  "| default=", p.get("default"), "| options=", (p.get("options") or [])[:8])
    except Exception as e:
        print(f"\n== {m} == ERROR {e}")

for m in ("suno", "lyria-3-5"):
    try:
        cap = pv.capabilities(m)
        print(f"\n== {m} ==")
        for p in (cap.get("params") or []):
            print("   -", p.get("key"), "|", p.get("label"), "| default=", p.get("default"),
                  "| options=", (p.get("options") or [])[:8])
    except Exception as e:
        print(f"\n== {m} == ERROR {e}")
