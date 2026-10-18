# -*- coding: utf-8 -*-
import json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
cat = json.load(open(os.path.join(HERE, "_pv_catalog_fresh.json"), encoding="utf-8"))
ms = cat["models"]
print("displayOnly:", collections.Counter(str(m.get("displayOnly")) for m in ms))
print("generationAvailable:", collections.Counter(str(m.get("generationAvailable")) for m in ms))
print("priceStatus:", collections.Counter(str(m.get("priceStatus")) for m in ms))
print("\n--- displayOnly=true or generationAvailable=false ---")
for m in ms:
    if m.get("displayOnly") or m.get("generationAvailable") is False:
        print(f"  {m.get('kind'):6s} {m['model']:32s} displayOnly={m.get('displayOnly')} genAvail={m.get('generationAvailable')} reason={str(m.get('unavailableReason'))[:60]} note={(m.get('note') or '')[:60]}")
print("\n--- note contains 'недоступ' ---")
for m in ms:
    if "недоступ" in (m.get("note") or ""):
        print(f"  {m.get('kind'):6s} {m['model']:32s} {(m.get('note') or '')[:90]}")
