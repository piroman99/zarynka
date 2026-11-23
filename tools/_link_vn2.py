# -*- coding: utf-8 -*-
"""Временные симлинки tools/{vn2,assets,out} -> ../{vn2,assets,out} для Playwright-регрессов.

Зачем: харнесс `_cdp` поднимает http-сервер с корнем `tools/` и просит `/vn2/index.html`,
а content.js ссылается на `../assets/...` и `../out/...` — без ссылок они дают 404
(видео значка и музыка сцен), и тесты падают на «js-ошибок нет».

Запуск: python3 tools/_link_vn2.py   (снять: --remove)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NAMES = ('vn2', 'assets', 'out')
remove = '--remove' in sys.argv

for n in NAMES:
    link = os.path.join(HERE, n)
    if remove:
        if os.path.islink(link):
            os.remove(link)
            print('удалён', link)
        continue
    if os.path.islink(link):
        print('уже есть', n, '->', os.readlink(link))
        continue
    os.symlink(os.path.relpath(os.path.join(ROOT, n), HERE), link)
    print('создан', n, '->', os.readlink(link))
