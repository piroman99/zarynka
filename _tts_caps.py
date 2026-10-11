# -*- coding: utf-8 -*-
import json, pv
c = pv.capabilities("gemini-3.8-flash-tts")
print(json.dumps(c, ensure_ascii=False, indent=2)[:3000])
