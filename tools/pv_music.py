import json, collections
d = json.load(open("_pv_media-catalog.json", encoding="utf-8"))

def best(m):
    vs = [v.get("honestPriceRub") or v.get("priceRub") for v in m.get("variants", []) or []]
    vs = [x for x in vs if isinstance(x, (int, float)) and x > 0]
    return min(vs) if vs else m.get("fromRub")

for kind in ("music", "audio"):
    lst = [m for m in d["models"] if m.get("kind") == kind]
    lst.sort(key=lambda m: (best(m) is None, best(m) or 0))
    print(f"\n######## {kind.upper()} ({len(lst)}) ########")
    for m in lst:
        print(f"  {m['model'][:36]:36s} {(('%.2f' % best(m)) if best(m) else 'n/a'):>8} ₽/{m.get('unit','?')[:12]:12s} {(m.get('note') or '')[:44]}")
