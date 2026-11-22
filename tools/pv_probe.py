import urllib.request, json, sys

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    return urllib.request.urlopen(req, timeout=30).read()

for url in ["https://plusvibeapi.ru/api/media-catalog",
            "https://plusvibeapi.ru/api/catalog"]:
    print("=" * 70)
    print("GET", url)
    try:
        raw = get(url)
        print("bytes:", len(raw))
        data = json.loads(raw)
        print("top keys:", list(data)[:20] if isinstance(data, dict) else f"list[{len(data)}]")
        open("_pv_" + url.split("/")[-1] + ".json", "wb").write(raw)
        print("saved _pv_" + url.split("/")[-1] + ".json")
    except Exception as e:
        print("ERR", type(e).__name__, e)
