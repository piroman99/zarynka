# -*- coding: utf-8 -*-
"""Доступность wall.delete групповому токену (на несуществующем посте)."""
import sys

sys.path.insert(0, "/home/ivan/.nanobot/workspace/novella/zaryanka")
import vk

gid = vk.whoami()["id"]
for label, kw in (
    ("plain", dict(owner_id=-gid, post_id=999999999)),
    ("group_id", dict(owner_id=-gid, post_id=999999999, group_id=gid)),
):
    try:
        vk.call("wall.delete", **kw)
        print("%-10s OK (неожиданно)" % label)
    except Exception as e:
        print("%-10s %s" % (label, str(e)[:110]))
