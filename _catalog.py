# -*- coding: utf-8 -*-
"""Сводка публичного каталога PlusVibe: доступные модели по видам + минимальная цена."""
import json, urllib.request, collections

BASE = "https://plusvibeapi.ru"

def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "nanobot-zaryanka/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

cat = get("/api/media-catalog")
models = cat.get("models", [])
by_kind = collections.defaultdict(list)
for m in models:
    by_kind[m.get("kind", "?")].append(m)

for kind in ("image", "video", "audio", "music", "3d"):
    lst = by_kind.get(kind, [])
    print(f"\n=== {kind} ({len(lst)}) ===")
    for m in lst:
        note = (m.get("note") or "").strip()
        flag = " [недоступно]" if "временно недоступ" in note else ""
        print(f"  {m.get('model'):28s} from={m.get('fromRub')} ед={m.get('unit')}{flag}")

pt = get("/api/media/price-table")
print("\nprice-table keys:", list(pt.keys())[:12] if isinstance(pt, dict) else type(pt))
