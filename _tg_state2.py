# -*- coding: utf-8 -*-
import sys, json, time
sys.path.insert(0, "/home/ivan/.nanobot/workspace/novella/zaryanka")
import tg

def try_call(meth, **kw):
    for i in range(4):
        try:
            return tg.call(meth, **kw)
        except Exception as e:
            last = e
            time.sleep(2 + i)
    return "FAIL: %s" % last

ch = try_call("getChat", chat_id=tg.CHANNEL)
if isinstance(ch, dict):
    print("channel:", ch.get("title"), ch.get("username"), "| linked_chat:", ch.get("linked_chat_id"))
else:
    print(ch)

print("member_count:", try_call("getChatMemberCount", chat_id=tg.CHANNEL))

me = try_call("getMe")
uid = me["id"]
print("bot id:", uid)
r = try_call("getChatMember", chat_id=tg.CHANNEL, user_id=uid)
print("bot member:", json.dumps(r, ensure_ascii=False)[:300] if isinstance(r, dict) else r)
