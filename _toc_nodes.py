import json, re, sys

src = open("vn2/content.js", encoding="utf-8").read()
i = src.index("{")
# strip "window.D = " prefix and trailing ";"
m = re.search(r"=\s*(\{.*\})\s*;?\s*$", src, re.S)
data = json.loads(m.group(1))

tot = 0
for ni, nd in enumerate(data["nodes"]):
    pages = nd.get("pages") or []
    tot += len(pages)
    first = (pages[0].get("tx") or "").split("\n")[0][:60] if pages else ""
    print(ni, nd.get("id"), nd.get("t"), len(pages), "|", first)
print("TOTAL SCENE PAGES", tot)
