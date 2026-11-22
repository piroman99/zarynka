# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, "/home/ivan/.nanobot/workspace/novella/zaryanka")
import tg

me = tg.call("getMe")
for cid, label in ((tg.CHANNEL, "channel"), (-1004313670543, "linked group")):
    try:
        r = tg.call("getChatMember", chat_id=cid, user_id=me["id"])
        print(label, "->", json.dumps(r, ensure_ascii=False)[:200])
    except Exception as e:
        print(label, "FAIL:", str(e)[:160])
