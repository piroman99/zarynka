# -*- coding: utf-8 -*-
import sys, json, os
sys.path.insert(0, "/home/ivan/.nanobot/workspace/novella/zaryanka")
import tg

me = tg.call("getMe")
print("bot:", me.get("username"), me.get("id"))

for uid in [me["id"]]:
    try:
        r = tg.call("getChatMember", chat_id=tg.CHANNEL, user_id=uid)
        print("member:", json.dumps(r, ensure_ascii=False))
    except Exception as e:
        print("member FAIL:", e)

for adm in [True, False]:
    try:
        r = tg.call("getChatAdministrators", chat_id=tg.CHANNEL)
        print("admins:", json.dumps(r, ensure_ascii=False)[:800])
        break
    except Exception as e:
        print("admins FAIL:", e)
