# -*- coding: utf-8 -*-
"""Музыка/3D + price-table из каталога PlusVibe."""
import json, urllib.request, collections

BASE = "https://plusvibeapi.ru"

def get(p):
    r = urllib.request.Request(BASE + p, headers={"User-Agent": "nanobot-zaryanka/1.0"})
    with urllib.request.urlopen(r, timeout=60) as f:
        return json.loads(f.read())

cat = get("/api/media-catalog")
by = collections.defaultdict(list)
for m in cat.get("models", []):
    by[m.get("kind", "?")].append(m)
print("KINDS:", {k: len(v) for k, v in by.items()})
for kind in ("music", "3d"):
    print(f"\n=== {kind} ===")
    for m in by.get(kind, []):
        print(f"  {m.get('model'):26s} from={m.get('fromRub')} ед={m.get('unit')}  {(m.get('note') or '')[:40]}")
pt = get("/api/media/price-table")
print("\nprice-table:", json.dumps(pt, ensure_ascii=False)[:600])
