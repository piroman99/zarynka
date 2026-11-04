# -*- coding: utf-8 -*-
import json, pv
for jid in ("cmvyalb6o00vhzx01x7ofvixn",):
    try:
        d = pv.job(jid)
        print(jid, json.dumps(d, ensure_ascii=False)[:900])
    except Exception as e:
        print(jid, "ERR", e)
