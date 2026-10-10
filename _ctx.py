# -*- coding: utf-8 -*-
"""Контекст вокруг реплики «подстригитесь» (к кому обращено)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
paras = [x.strip() for x in open(os.path.join(HERE, "assets", "story.txt"), encoding="utf-8").read().split("\n") if x.strip()]
for i in range(52, 62):
    print(f"#{i}: {paras[i][:500]}\n")
