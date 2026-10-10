import json
d = json.load(open("_pv_media-catalog.json", encoding="utf-8"))
m = d["models"][:2]
print(json.dumps(m, ensure_ascii=False, indent=2)[:4000])
