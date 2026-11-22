import os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
p = os.path.join(ROOT, "assets", "final", "prolog", "p8_v4b_bak.png")
if os.path.exists(p):
    os.remove(p)
    print("убран дубль:", os.path.relpath(p, HERE))
g = os.path.join(ROOT, "assets", "gen", "prolog_p8v4_b__gpt-image-2_0.png")
print("мастер B на месте:", os.path.exists(g), os.path.getsize(g) if os.path.exists(g) else 0)
