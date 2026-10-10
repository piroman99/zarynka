import json, collections

d = json.load(open("_pv_media-catalog.json", encoding="utf-8"))
models = d["models"]

def best_price(m):
    vals = []
    for v in m.get("variants", []) or []:
        p = v.get("honestPriceRub") or v.get("priceRub")
        if isinstance(p, (int, float)) and p > 0:
            vals.append(p)
    if vals:
        return min(vals)
    return m.get("fromRub")

by_kind = collections.defaultdict(list)
for m in models:
    by_kind[m.get("kind", "?")].append(m)

for kind in ("image", "video"):
    lst = by_kind.get(kind, [])
    lst.sort(key=lambda m: (best_price(m) is None, best_price(m) or 0))
    print(f"\n{'#'*8} {kind.upper()}  ({len(lst)})  {'#'*8}")
    for m in lst:
        p = best_price(m)
        note = (m.get("note") or "")[:34]
        ins = ",".join(m.get("inputTypes", []))
        print(f"  {m['model'][:34]:34s} {('%.2f' % p) if p else '  n/a':>8} ₽/{m.get('unit','?')[:10]:10s} in=[{ins[:18]:18s}] {note}")
