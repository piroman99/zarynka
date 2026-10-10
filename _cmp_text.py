# -*- coding: utf-8 -*-
"""Сравнить «Original text» из старого репо с нашим assets/story.txt."""
import os, difflib

HERE = os.path.dirname(os.path.abspath(__file__))
old_p = os.path.join(HERE, "assets", "orig", "zarynka_2016", "Original text")
new_p = os.path.join(HERE, "assets", "story.txt")

raw = open(old_p, "rb").read()
for enc in ("utf-8", "cp1251", "utf-16"):
    try:
        old = raw.decode(enc)
        print("decoded as", enc, "->", len(old), "chars")
        break
    except Exception:
        continue

new = open(new_p, encoding="utf-8").read()
print("story.txt:", len(new), "chars")


def norm(t):
    return "\n".join(x.strip() for x in t.replace("\r\n", "\n").split("\n") if x.strip())


o, n = norm(old), norm(new)
print("old paras:", o.count("\n") + 1, " new paras:", n.count("\n") + 1)
print("identical:", o == n)
if o != n:
    sm = difflib.SequenceMatcher(None, o, n)
    print("similarity ratio:", round(sm.ratio(), 3))
    # первые расхождения
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            print(f"[{tag}] old[{i1}:{i2}]={o[i1:i2][:160]!r}  new[{j1}:{j2}]={n[j1:j2][:160]!r}")
            if tag in ("delete", "replace"):
                pass
print("\n--- head old ---")
print(o[:400])
print("--- tail old ---")
print(o[-400:])
