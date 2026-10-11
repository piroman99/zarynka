import urllib.request, ssl, socket

HOSTS = [
    ("2061.su (конкурс СССР-2061)", "https://2061.su/"),
    ("author.today (рассказ)", "https://author.today/reader/23050/166908"),
    ("vk.ru (сообщество)", "https://vk.ru/zaryanka_vn"),
    ("plusvibeapi.ru (генератор)", "https://plusvibeapi.ru/v1"),
    ("web.archive.org (архив)", "https://web.archive.org/"),
    ("max.ru", "https://max.ru/"),
]
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
for name, url in HOSTS:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
            print("OK  %-32s -> %s  (%d b)" % (name, r.status, len(r.read(2000))))
    except Exception as e:
        print("ERR %-32s -> %s" % (name, type(e).__name__ + ": " + str(e)[:90]))
