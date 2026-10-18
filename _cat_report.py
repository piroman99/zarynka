# -*- coding: utf-8 -*-
"""Compact availability report from the fresh catalog."""
import json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
cat = json.load(open(os.path.join(HERE, "_pv_catalog_fresh.json"), encoding="utf-8"))
ms = cat["models"]
print("flags:", {k: v for k, v in cat.items() if k != "models"})

live = collections.defaultdict(list)
dead = collections.defaultdict(list)
for m in ms:
    k = m.get("kind", "?")
    ga = m.get("generationAvailable")
    reason = m.get("unavailableReason") or m.get("priceUnavailable") or m.get("note")
    if ga is False:
        dead[k].append((m["model"], str(reason)[:70]))
    else:
        live[k].append((m["model"], m.get("fromRub"), m.get("priceStatus"), m.get("aliases"), len(m.get("deprecatedAliases") or [])))

for k in ("image", "video", "music", "audio", "3d"):
    print(f"\n==== {k}: LIVE {len(live[k])} / DEAD {len(dead[k])} ====")
    print("-- live --")
    for name, fr, ps, al, ndep in sorted(live[k], key=lambda t: (t[1] or 999)):
        extra = []
        if al:
            extra.append("aliases=" + ",".join(al))
        if ndep:
            extra.append(f"deprecated={ndep}")
        if ps and ps not in ("ok", "exact"):
            extra.append(f"price={ps}")
        print(f"  {name:36s} {('%.2f' % fr) if isinstance(fr,(int,float)) else 'n/a':>8}  " + " ".join(extra))
    if dead[k]:
        print("-- dead --")
        for name, reason in dead[k]:
            print(f"  {name:36s} {reason}")
