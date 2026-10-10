import urllib.request, json, os, sys

PUB = "https://disk.yandex.ru/d/0oYY_-lGvJegj"
API = "https://cloud-api.yandex.net/v1/disk/public/resources"

def api(path="/", limit=200):
    import urllib.parse
    q = urllib.parse.urlencode({"public_key": PUB, "path": path, "limit": limit})
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req, timeout=30))

try:
    root = api("/")
except Exception as e:
    print("NET_ERR", type(e).__name__, e); sys.exit(1)

print("NAME:", root.get("name"), "type:", root.get("type"))
def walk(path="/", depth=0):
    try:
        r = api(path)
    except Exception as e:
        print("  " * depth + f"[err {path}] {e}"); return
    for it in r.get("_embedded", {}).get("items", []):
        t = it["type"]
        nm = it["name"]
        if t == "dir":
            print("  " * depth + f"DIR  {it['path']}")
            if depth < 6:
                walk(it["path"], depth + 1)
        else:
            print("  " * depth + f"FILE {it['path']}  ({it.get('size')} b, {it.get('mime_type')})")
walk("/")
