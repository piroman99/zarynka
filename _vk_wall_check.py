# -*- coding: utf-8 -*-
"""Проверка стены сообщества через headless Chromium (--dump-dom).

Групповой токен ВК не даёт wall.get (error 27), поэтому читаем DOM страницы.
Запуск: python3 _vk_wall_check.py [фрагмент-текста]
"""
import glob
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
URL = "https://vk.ru/zaryanka_vn"
NEEDLE = sys.argv[1] if len(sys.argv) > 1 else "Как звучит приёмная"

r = subprocess.run([CHROME, '--headless=new', '--no-sandbox',
                    '--disable-dev-shm-usage', '--disable-gpu',
                    '--window-size=1280,2000',
                    '--virtual-time-budget=15000',
                    '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/140.0 Safari/537.36',
                    '--dump-dom', URL],
                   capture_output=True, text=True, timeout=180)
html = r.stdout
print("dom bytes:", len(html), "| stderr tail:", r.stderr.strip().splitlines()[-1:] or "-")

text = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
text = re.sub(r"<style.*?</style>", " ", text, flags=re.S)
text = re.sub(r"<br\s*/?>", "\n", text)
text = re.sub(r"<[^>]+>", "\n", text)
text = re.sub(r"&quot;", '"', text)
text = re.sub(r"&#39;|&apos;", "'", text)
text = re.sub(r"&amp;", "&", text)
lines = [l.strip() for l in text.splitlines() if l.strip()]
print("lines:", len(lines))

hit = [i for i, l in enumerate(lines) if NEEDLE in l]
print("совпадений с %r: %d" % (NEEDLE, len(hit)))
for i in hit:
    print("---- контекст ----")
    print("\n".join(lines[max(0, i - 3):i + 14])[:1400])
if not hit:
    print("---- первые 80 строк ----")
    print("\n".join(lines[:80])[:2500])
