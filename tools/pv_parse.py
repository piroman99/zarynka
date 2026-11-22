import json, collections

d = json.load(open("_pv_media-catalog.json", encoding="utf-8"))
print("flags:", {k: d[k] for k in d if k != "models"})
models = d["models"]
print("media models:", len(models), "type:", type(models))
if isinstance(models, dict):
    items = list(models.items())
else:
    items = [(m.get("id") or m.get("name"), m) for m in models]

by_kind = collections.defaultdict(list)
for mid, m in items:
    kind = m.get("kind") or m.get("type") or "?"
    by_kind[kind].append((mid, m))

for kind in sorted(by_kind):
    lst = by_kind[kind]
    print(f"\n######## {kind}  ({len(lst)}) ########")
    for mid, m in lst[:60]:
        price = m.get("fromRub") or m.get("from_rub") or m.get("price") or m.get("priceFrom")
        name = m.get("name") or m.get("title") or ""
        variants = m.get("variants")
        vn = len(variants) if isinstance(variants, list) else ""
        print(f"  {str(mid)[:55]:55s} {str(price):>10} {str(name)[:40]:40s} v={vn}")
