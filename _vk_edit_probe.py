# -*- coding: utf-8 -*-
"""Почему wall.edit отдаёт error 27: проверяем на НЕСУЩЕСТВУЮЩЕМ посту.

Если метод групповому токену доступен — ВК ответит ошибкой 100 («нет такого поста»),
если недоступен — ошибкой 27. Текст живого поста не трогаем.
"""
import sys

sys.path.insert(0, "/home/ivan/.nanobot/workspace/novella/zaryanka")
import vk

gid = vk.whoami()["id"]
FAKE = 999999999
print("group:", gid)

tries = [
    ("plain", dict(owner_id=-gid, post_id=FAKE, message="probe")),
    ("group_id", dict(owner_id=-gid, post_id=FAKE, message="probe", group_id=gid)),
    ("from_group", dict(owner_id=-gid, post_id=FAKE, message="probe", from_group=1)),
]
for label, kw in tries:
    try:
        vk.call("wall.edit", **kw)
        print("%-10s OK (неожиданно)" % label)
    except Exception as e:
        print("%-10s %s" % (label, str(e)[:110]))
