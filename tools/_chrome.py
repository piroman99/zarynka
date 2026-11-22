# -*- coding: utf-8 -*-
"""Путь к Chromium для headless-проверок — один на все скрипты.

Раньше каждый скрипт считал его сам: `HERE/../..` + `.playwright-browsers`.
После переезда скриптов из корня репозитория в `tools/` этот путь стал на
уровень короче, и Chromium «пропадал» (IndexError: list index out of range)
в семи файлах сразу. Теперь путь ищется ВВЕРХ от каталога файла — раскладка
больше не важна.
"""
import glob
import os

HERE = os.path.dirname(os.path.abspath(__file__))
UP = 6          # на сколько уровней вверх искать .playwright-browsers


def find_chrome():
    d = HERE
    for _ in range(UP):
        hits = glob.glob(os.path.join(d, '.playwright-browsers', 'chromium-*',
                                      'chrome-linux64', 'chrome'))
        if hits:
            return hits[0]
        d = os.path.dirname(d)
    raise RuntimeError('Chromium не найден: нет .playwright-browsers выше ' + HERE)


CHROME = find_chrome()
